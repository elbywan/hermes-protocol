const ref = require('ref')
const array = require('ref-array')
const Casteable = require('./Casteable')
const { cast } = require('../tools')
const DoubleArray = require('./DoubleArray')
const {
    CSlot,
    CSlotValue,
    CNluSlot,
    CNluSlotArray,
    CInstantTimeValue,
    CTimeIntervalValue,
    CAmountOfMoneyValue,
    CTemperatureValue,
    CDurationValue
} = require('../ffi/typedefs')

const SlotsArrayType = array(ref.refType(CNluSlot))

function castSlot (slot) {
    const slotContents = cast(slot.nlu_slot.deref(), {
        value: function (slotValue) {
            const value_type = slotValue.value_type
            let valuePtr = slotValue.value
            let value
            switch(value_type) {
                case 1:
                    value = valuePtr.readCString()
                    break
                case 2:
                    valuePtr = ref.reinterpret(valuePtr, ref.types.double.size)
                    value = ref.get(valuePtr, 0, 'double')
                    break
                case 3:
                    valuePtr = ref.reinterpret(valuePtr, ref.types.int.size)
                    value = ref.get(valuePtr, 0, 'int')
                    break
                case 4:
                    valuePtr = ref.reinterpret(valuePtr, CInstantTimeValue.size)
                    value = ref.get(valuePtr, 0, CInstantTimeValue)
                    break
                case 5:
                    valuePtr = ref.reinterpret(valuePtr, CTimeIntervalValue.size)
                    value = ref.get(valuePtr, 0, CTimeIntervalValue)
                    break
                case 6:
                    valuePtr = ref.reinterpret(valuePtr, CAmountOfMoneyValue.size)
                    value = ref.get(valuePtr, 0, CAmountOfMoneyValue)
                    break
                case 7:
                    valuePtr = ref.reinterpret(valuePtr, CTemperatureValue.size)
                    value = ref.get(valuePtr, 0, CTemperatureValue)
                    break
                case 8:
                    valuePtr = ref.reinterpret(valuePtr, CDurationValue.size)
                    value = ref.get(valuePtr, 0, CDurationValue)
                    break
                case 9:
                    valuePtr = ref.reinterpret(valuePtr, ref.types.double.size)
                    value = ref.get(valuePtr, 0, 'double')
                    break
                default:
                    value = null
            }
            return {
                value_type,
                value
            }
        }
    })

    return {
        confidence: slot.confidence,
        ...slotContents
    }
}

class SlotArray extends Casteable {
    constructor(arg) {
        super({})
        if(arg instanceof Buffer) {
            this._array = new DoubleArray(arg, {
                itemArrayType: CNluSlotArray,
                refArrayType: SlotsArrayType,
                cast: castSlot
            })._array
        } else {
            this._array = arg
        }
    }
    forge() {
        const forgeSlotPtr = slot => (
            new Casteable(slot).forge(CSlot, {
                value: slotValue => new Casteable(slotValue).forge(CSlotValue, {
                    value: value => {
                        const value_type = slotValue.value_type
                        let valuePtr = ref.NULL
                        switch(value_type) {
                            case 1:
                                valuePtr = ref.allocCString(value)
                                break
                            case 2:
                                valuePtr = ref.alloc('double', value)
                                break
                            case 3:
                                valuePtr = ref.alloc('int', value)
                                break
                            case 4:
                                valuePtr = new Casteable(value).forge(CInstantTimeValue)
                                break
                            case 5:
                                valuePtr = new Casteable(value).forge(CTimeIntervalValue)
                                break
                            case 6:
                                valuePtr = new Casteable(value).forge(CAmountOfMoneyValue)
                                break
                            case 7:
                                valuePtr = new Casteable(value).forge(CTemperatureValue)
                                break
                            case 8:
                                valuePtr = new Casteable(value).forge(CDurationValue)
                                break
                            case 9:
                                valuePtr = ref.alloc('double', value)
                                break
                            default:
                                valuePtr = ref.NULL
                        }
                        return valuePtr
                    }
                })
            }).ref()
        )

        return new DoubleArray(this._array, {
            itemArrayType: CNluSlotArray,
            refArrayType: SlotsArrayType,
            forge: ({ confidence, ...rest }) => (
                new Casteable({ confidence, nlu_slot: { ...rest }}).forge(CNluSlot, {
                    nlu_slot: forgeSlotPtr
                }).ref()
            )
        }).forge()
    }
}

module.exports = SlotArray