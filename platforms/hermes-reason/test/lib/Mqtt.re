open TestFramework;
open HermesReason;
open Structs;
open Enums;
open Tools;

let port = ref(0);

let testPublish = (~expect, ~hermes, ~topic, callback) =>
  try(
    expect.string(receiveMessage(~port=port^, topic, () => callback(hermes))).
      toMatchSnapshot()
  ) {
  | e =>
    Printexc.print_backtrace(stderr);
    raise(e);
  };

let testSubscribe = (~expect, ~hermes, ~topic, ~name, subscription) =>
  try(
    {
      hermes
      |> subscription
      |> (_ => readMessage("./test/lib/messages/" ++ name ++ ".json"))
      |> publishMessage(~port=port^, topic)
      |> ignore;

      Unix.sleepf(0.2);

      expect.assertions(1);
    }
  ) {
  | e =>
    Printexc.print_backtrace(stderr);
    raise(e);
  };

/* Unix.putenv("RUST_LOG", "debug"); */

let {describe, describeSkip, describeOnly} =
  describeConfig
  |> withLifecycle(testLifecycle => {
       testLifecycle
       |> beforeAll(() => {
            port := findOpenPort();
            let pid = launchMosquitto(~silent=true, port^);
            /* Give some time to mosquitto… */
            Unix.sleepf(0.5);
            try({
              let hermes =
                Hermes.make(
                  ~libraryPath="../../target/debug/libhermes_mqtt_ffi",
                  ~debug=false,
                  ~options={
                    ...Hermes.defaultOptions,
                    broker_address: "localhost:" ++ string_of_int(port^),
                  },
                  (),
                );
              (pid, hermes);
            }) {
            | fail =>
              killMosquitto(pid);
              raise(fail);
            };
          })
       |> afterAll(((mosquittoPid, hermes)) => {
            Hermes.destroy(hermes);
            killMosquitto(mosquittoPid);
          })
       |> beforeEach(((_, hermes)) => hermes)
     })
  |> build;

describe("High Level Api", ({describe}) => {
  describe("Publish messages", ({test, testSkip}) => {
    test("Start session", ({expect, env: hermes}) => {
      testPublish(
        ~expect,
        ~hermes,
        ~topic="hermes/dialogueManager/startSession",
        Dialog.Publish.startSession({
          init:
            Action({
              text: Some("toto"),
              intent_filter: Some(["intent", "filter"]),
              can_be_enqueued: true,
              send_intent_not_recognized: false,
            }),
          custom_data: Some("customThing"),
          site_id: "siteId",
        }),
      )
    });

    test("Continue session", ({expect, env: hermes}) => {
      testPublish(
        ~expect,
        ~hermes,
        ~topic="hermes/dialogueManager/continueSession",
        Dialog.Publish.continueSession({
          session_id: "session id",
          text: Some("text"),
          intent_filter: Some(["intentA", "intentB"]),
          custom_data: None,
          slot: None,
          send_intent_not_recognized: true,
        }),
      )
    });

    test("End session", ({expect, env: hermes}) => {
      testPublish(
        ~expect,
        ~hermes,
        ~topic="hermes/dialogueManager/endSession",
        Dialog.Publish.endSession({
          session_id: "session id",
          text: Some("Session ended"),
        }),
      )
    });

    test("Configure dialog", ({expect, env: hermes}) => {
      testPublish(
        ~expect,
        ~hermes,
        ~topic="hermes/dialogueManager/configure",
        Dialog.Publish.configure({
          site_id: Some("default"),
          intents:
            Some([
              {intent_id: "intent1", enable: true},
              {intent_id: "intent2", enable: false},
              {intent_id: "intent3", enable: false},
            ]),
        }),
      )
    });

    test("Injection request", ({expect, env: hermes}) => {
      testPublish(
        ~expect,
        ~hermes,
        ~topic="hermes/injection/perform",
        Injection.Publish.injectionRequest({
          id: Some("abcdef"),
          cross_language: Some("en"),
          lexicon: [
            {
              key: "films",
              values: ["The Wolf of Wall Street", "The Lord of the Rings"],
            },
          ],
          operations: [
            {
              kind: SNIPS_INJECTION_KIND_ADD,
              values: [
                {
                  key: "films",
                  values: [
                    "The Wolf of Wall Street",
                    "The Lord of the Rings",
                  ],
                },
              ],
            },
          ],
        }),
      )
    });

    test("Injection status request", ({expect, env: hermes}) => {
      testPublish(
        ~expect,
        ~hermes,
        ~topic="hermes/injection/statusRequest",
        Injection.Publish.injectionStatusRequest,
      )
    });

    test("Toggle sound feedback on", ({expect, env: hermes}) => {
      testPublish(
        ~expect,
        ~hermes,
        ~topic="hermes/feedback/sound/toggleOn",
        SoundFeedback.Publish.toggleOn({
          site_id: "default",
          session_id: Some("id"),
        }),
      )
    });

    test("Toggle sound feedback off", ({expect, env: hermes}) => {
      testPublish(
        ~expect,
        ~hermes,
        ~topic="hermes/feedback/sound/toggleOff",
        SoundFeedback.Publish.toggleOff({
          site_id: "default",
          session_id: Some("id"),
        }),
      )
    });

    testSkip("Register sound", ({expect, env: hermes}) => {
      let wav_bytes_list = [0, 1, 2, 3];

      testPublish(
        ~expect,
        ~hermes,
        ~topic="hermes/tts/registerSound/foo:bar",
        Tts.Publish.registerSound({
          sound_id: "foo:bar",
          wav_sound: wav_bytes_list |> List.map(Unsigned.UInt8.of_int),
        }),
      );
    });
  });

  describe("Subscribe to messages", ({test}) => {
    test("Session started", ({expect, env: hermes}) => {
      testSubscribe(
        ~expect,
        ~hermes,
        ~topic="hermes/dialogueManager/sessionStarted",
        ~name="SessionStarted",
        Dialog.Subscribe.sessionStarted(~once=true, ~callback=msg => {
          expect.equal(Messages.sessionStarted, msg)
        }),
      )
    });

    test("Session queued", ({expect, env: hermes}) => {
      testSubscribe(
        ~expect,
        ~hermes,
        ~topic="hermes/dialogueManager/sessionQueued",
        ~name="SessionQueued",
        Dialog.Subscribe.sessionQueued(~once=true, ~callback=msg => {
          expect.equal(Messages.sessionQueued, msg)
        }),
      )
    });

    test("Session ended", ({expect, env: hermes}) => {
      testSubscribe(
        ~expect,
        ~hermes,
        ~topic="hermes/dialogueManager/sessionEnded",
        ~name="SessionEnded",
        Dialog.Subscribe.sessionEnded(~once=true, ~callback=msg => {
          expect.equal(Messages.sessionEnded, msg)
        }),
      )
    });

    test("Intent not recognized", ({expect, env: hermes}) => {
      testSubscribe(
        ~expect,
        ~hermes,
        ~topic="hermes/dialogueManager/intentNotRecognized",
        ~name="IntentNotRecognized",
        Dialog.Subscribe.intentNotRecognized(~once=true, ~callback=msg => {
          expect.equal(Messages.intentNotRecognized, msg)
        }),
      )
    });

    test("Intent received - specific", ({expect, env: hermes}) => {
      testSubscribe(
        ~expect,
        ~hermes,
        ~topic="hermes/intent/jelb:lightsColor",
        ~name="Intent",
        Dialog.Subscribe.intent(
          ~once=true, ~intent="jelb:lightsColor", ~callback=msg => {
          expect.equal(Messages.intentMessage, msg)
        }),
      )
    });

    test("Intent received - any", ({expect, env: hermes}) => {
      testSubscribe(
        ~expect,
        ~hermes,
        ~topic="hermes/intent/jelb:lightsColor",
        ~name="Intent",
        Dialog.Subscribe.intents(~once=true, ~callback=msg => {
          expect.equal(Messages.intentMessage, msg)
        }),
      )
    });

    test("Injection complete", ({expect, env: hermes}) => {
      testSubscribe(
        ~expect,
        ~hermes,
        ~topic="hermes/injection/complete",
        ~name="InjectionComplete",
        Injection.Subscribe.injectionComplete(~once=true, ~callback=msg => {
          expect.equal(Messages.injectionComplete, msg)
        }),
      )
    });

    test("Injection reset complete", ({expect, env: hermes}) => {
      testSubscribe(
        ~expect,
        ~hermes,
        ~topic="hermes/injection/reset/complete",
        ~name="InjectionResetComplete",
        Injection.Subscribe.injectionResetComplete(~once=true, ~callback=msg => {
          expect.equal(Messages.injectionResetComplete, msg)
        }),
      )
    });

    test("Injection status", ({expect, env: hermes}) => {
      testSubscribe(
        ~expect,
        ~hermes,
        ~topic="hermes/injection/status",
        ~name="InjectionStatus",
        Injection.Subscribe.injectionStatus(~once=true, ~callback=msg => {
          expect.equal(Messages.injectionStatus, msg)
        }),
      )
    });
  });
});