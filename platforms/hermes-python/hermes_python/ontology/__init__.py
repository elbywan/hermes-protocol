from enum import IntEnum
from hermes_python.ffi.ontology import SNIPS_HERMES_COMPONENT


class HermesComponent(IntEnum):
    AUDIO_SERVER = 1
    HOTWORD = 2
    ASR = 3
    NLU = 4
    DIALOGUE = 5
    TTS = 6
    INJECTION = 7
    CLIENT_APP = 8

    @classmethod
    def from_c_repr(cls, c_repr):
        # type: (SNIPS_HERMES_COMPONENT) -> HermesComponent
        if c_repr.SNIPS_HERMES_COMPONENT_NONE:
            raise Exception("Bad value type. Got : {}".format(c_repr))
        else:
            return HermesComponent(c_repr.value)


class MqttOptions(object):
    def __init__(self,
                 broker_address="localhost:1883",
                 username=None, password=None,
                 tls_hostname=None, tls_ca_file=None, tls_ca_path=None, tls_client_key=None, tls_client_cert=None,
                 tls_disable_root_store=False):
        """
        :param broker_address: Address of the MQTT broker in the form 'ip:port'
        :param username: Username to use on the broker. Nullable
        :param password: Password to use on the broker. Nullable
        :param tls_hostname: Hostname to use for the TLS configuration. Nullable, setting a value enables TLS
        :param tls_ca_file: CA files to use if TLS is enabled. Nullable
        :param tls_ca_path: CA path to use if TLS is enabled. Nullable
        :param tls_client_key: Client key to use if TLS is enabled. Nullable
        :param tls_client_cert: Client cert to use if TLS is enabled. Nullable
        :param tls_disable_root_store: Boolean indicating if the root store should be disabled if TLS is enabled.
        """
        self.broker_address = broker_address

        self.username = username
        self.password = password

        self.tls_hostname = tls_hostname
        self.tls_ca_file = tls_ca_file
        self.tls_ca_path = tls_ca_path
        self.tls_client_key = tls_client_key
        self.tls_client_cert = tls_client_cert
        self.tls_disable_root_store = tls_disable_root_store
