from __future__ import unicode_literals
import mock
import pytest

from hermes_python.hermes import Hermes
from hermes_python.ontology import MqttOptions
from hermes_python.ontology.dialogue import StartSessionMessage, SessionInitNotification, ContinueSessionMessage
from hermes_python.ontology.injection import InjectionRequestMessage

HOST = "localhost"
DUMMY_INTENT_NAME = "INTENT"


def test_initialization():
    h = Hermes(HOST)
    assert 0 == len(h.ffi.dialogue._c_callback_subscribe_intent)


def test_initialization_with_options():
    mqtt_opts = MqttOptions()
    h = Hermes(mqtt_options=mqtt_opts)
    assert h.mqtt_options.broker_address == "localhost:1883"


def test_context_manager_enter_calls_ffi_api():
    h = Hermes(HOST)
    h.ffi = mock.MagicMock()

    h.__enter__()
    h.__exit__(None, None, None)

    h.ffi.establish_connection.assert_called_once()
    h.ffi.release_connection.assert_called_once()


@mock.patch("hermes_python.api.ffi.tts.hermes_drop_tts_facade")
@mock.patch("hermes_python.api.ffi.tts.hermes_protocol_handler_tts_facade")
@mock.patch("hermes_python.api.ffi.injection.hermes_drop_injection_facade")
@mock.patch("hermes_python.api.ffi.injection.hermes_protocol_handler_injection_facade")
@mock.patch("hermes_python.api.ffi.feedback.hermes_drop_sound_feedback_facade")
@mock.patch("hermes_python.api.ffi.feedback.hermes_protocol_handler_sound_feedback_facade")
@mock.patch("hermes_python.api.ffi.dialogue.hermes_drop_dialogue_facade")
@mock.patch("hermes_python.api.ffi.dialogue.hermes_protocol_handler_dialogue_facade")
@mock.patch("hermes_python.api.ffi.hermes_destroy_mqtt_protocol_handler")
@mock.patch("hermes_python.api.ffi.hermes_protocol_handler_new_mqtt_with_options")
def test_context_manager_enter_exit(hermes_protocol_handler_new_mqtt,
                                    hermes_destroy_mqtt_protocol_handler,
                                    hermes_protocol_handler_dialogue_facade, hermes_drop_dialogue_facade,
                                    hermes_protocol_handler_sound_feedback_facade, hermes_drop_sound_feedback_facade,
                                    hermes_protocol_handler_injection_facade, hermes_drop_injection_facade,
                                    hermes_protocol_handler_tts_facade, hermes_drop_tts_facade):
    with Hermes(HOST) as h:
        pass

    hermes_protocol_handler_new_mqtt.assert_called_once()

    hermes_protocol_handler_dialogue_facade.assert_called_once()
    hermes_drop_dialogue_facade.assert_called_once()

    hermes_protocol_handler_sound_feedback_facade.assert_called_once()
    hermes_drop_sound_feedback_facade.assert_called_once()

    hermes_protocol_handler_injection_facade.assert_called_once()
    hermes_drop_injection_facade.assert_called_once()

    hermes_protocol_handler_tts_facade.assert_called_once()
    hermes_drop_tts_facade.assert_called_once()

    hermes_destroy_mqtt_protocol_handler.assert_called_once()


@mock.patch("hermes_python.api.ffi.feedback.hermes_protocol_handler_sound_feedback_facade")
@mock.patch("hermes_python.api.ffi.dialogue.hermes_protocol_handler_dialogue_facade")
@mock.patch("hermes_python.api.ffi.dialogue.hermes_drop_dialogue_facade")
@mock.patch("hermes_python.api.ffi.hermes_protocol_handler_new_mqtt_with_options")
def test_context_manager_catches_exceptions(hermes_protocol_handler_new_mqtt, mocked_hermes_drop_dialogue_facade,
                                            hermes_protocol_handler_dialogue_facade,
                                            hermes_protocol_handler_sound_feedback_facade):
    hermes_protocol_handler_dialogue_facade.side_effect = Exception("An exception occured!")

    with pytest.raises(Exception):
        with Hermes(HOST) as h:
            pass


def test_subscribe_intent_correctly_registers_callback():
    def user_callback(hermes, intentMessage):
        pass

    h = Hermes(HOST)
    h.ffi = mock.MagicMock()
    h.__enter__()
    h.subscribe_intent(DUMMY_INTENT_NAME, user_callback)
    h.__exit__(None, None, None)
    h.ffi.dialogue.register_subscribe_intent_handler.assert_called_once_with(DUMMY_INTENT_NAME, user_callback, h)


def test_subscribe_intents_correctly_registers_callback():
    def user_callback(hermes, intentMessage):
        pass

    h = Hermes(HOST)
    h.ffi = mock.MagicMock()
    h.__enter__()
    h.subscribe_intents(user_callback)
    h.__exit__(None, None, None)

    h.ffi.establish_connection.assert_called_once()
    h.ffi.dialogue.register_subscribe_intents_handler.assert_called_once_with(user_callback, h)


def test_subscribe_session_started_correctly_registers_callback():
    def user_callback(hermes, intentMessage):
        pass

    h = Hermes(HOST)
    h.ffi = mock.MagicMock()
    h.__enter__()
    h.subscribe_session_started(user_callback)
    h.__exit__(None, None, None)

    h.ffi.establish_connection.assert_called_once()
    h.ffi.dialogue.register_session_started_handler.assert_called_once_with(user_callback, h)


def test_subscribe_session_queued_correctly_registers_callback():
    def user_callback(hermes, intentMessage):
        pass

    h = Hermes(HOST)
    h.ffi = mock.MagicMock()
    h.__enter__()
    h.subscribe_session_queued(user_callback)
    h.__exit__(None, None, None)

    h.ffi.establish_connection.assert_called_once()
    h.ffi.dialogue.register_session_queued_handler.assert_called_once_with(user_callback, h)


def test_subscribe_session_ended_correctly_registers_callback():
    def user_callback(hermes, intentMessage):
        pass

    h = Hermes(HOST)
    h.ffi = mock.MagicMock()
    h.__enter__()
    h.subscribe_session_ended(user_callback)
    h.__exit__(None, None, None)

    h.ffi.establish_connection.assert_called_once()
    h.ffi.dialogue.register_session_ended_handler.assert_called_once_with(user_callback, h)


def test_subscribe_intent_not_recognized_correctly_registers_callback():
    def user_callback(hermes, intentMessage):
        pass

    h = Hermes(HOST)
    h.ffi = mock.MagicMock()
    h.__enter__()
    h.subscribe_intent_not_recognized(user_callback)
    h.__exit__(None, None, None)

    h.ffi.establish_connection.assert_called_once()
    h.ffi.dialogue.register_intent_not_recognized_handler.assert_called_once_with(user_callback, h)


def test_start_session_notification_1():
    h = Hermes(HOST)
    h.ffi = mock.MagicMock()

    with h:
        h.publish_start_session_notification(None, "welcome !", "custom_data")

    start_session_notification_message = StartSessionMessage(SessionInitNotification("welcome !"), "custom_data", None)
    h.ffi.dialogue.publish_start_session.assert_called_once_with(start_session_notification_message)


def test_start_session_notification_2():
    h = Hermes(HOST)
    h.ffi = mock.MagicMock()

    with h:
        h.publish_start_session_notification(None, None, "custom_data", "yup!")

    start_session_notification_message = StartSessionMessage(SessionInitNotification("yup!"), "custom_data", None)
    h.ffi.dialogue.publish_start_session.assert_called_once_with(start_session_notification_message)


def test_start_session_notification_text_parameter_takes_precedence_over_session_initiation_text():
    h = Hermes(HOST)
    h.ffi = mock.MagicMock()

    with h:
        h.publish_start_session_notification(None, "test", "custom_data", "yup!")

    start_session_notification_message = StartSessionMessage(SessionInitNotification("yup!"), "custom_data", None)
    h.ffi.dialogue.publish_start_session.assert_called_once_with(start_session_notification_message)


class TestContinueSession(object):
    def test_continue_session_slot_filler(self):
        h = Hermes(HOST)
        h.ffi = mock.MagicMock()

        with h:
            h.publish_continue_session("session_id", "Tell me what the missing slot is", ["intent1"], None, False,
                                       "missing_slot")

        continue_session_message = ContinueSessionMessage("session_id", "Tell me what the missing slot is", ["intent1"],
                                                          None, False, "missing_slot")
        h.ffi.dialogue.publish_continue_session.assert_called_once_with(continue_session_message)


class TestInjection(object):
    # These tests are disabled as long as the injection API is stabilized.
    # def test_requesting_injection_status(self):
    #     h = Hermes(HOST)
    #     h.ffi = mock.MagicMock()
    #
    #
    #     with h:
    #         h.request_injection_status()
    #
    #     h.ffi.injection.publish_injection_status_request.assert_called_once()
    #
    # def test_correctly_subscribing_to_injection_status(self):
    #     def injection_request_cb(callback, injection_status):
    #         pass
    #
    #     h = Hermes(HOST)
    #     h.ffi = mock.MagicMock()
    #
    #     with h:
    #         h.subscribe_injection_status(injection_request_cb)
    #
    #     h.ffi.injection.register_subscribe_injection_status.assert_called_once_with(injection_request_cb, h)

    def test_correctly_requesting_injection(self):
        h = Hermes(HOST)
        h.ffi = mock.MagicMock()

        injection_request = InjectionRequestMessage([], dict())

        with h:
            h.request_injection(injection_request)

        h.ffi.injection.publish_injection_request.assert_called_once_with(injection_request)
