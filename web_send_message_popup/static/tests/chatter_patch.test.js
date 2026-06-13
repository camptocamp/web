import {
    asyncStep,
    mockService,
    patchWithCleanup,
    waitForSteps,
} from "@web/../tests/web_test_helpers";
import {
    contains,
    defineMailModels,
    openFormView,
    registerArchs,
    start,
    startServer,
} from "@mail/../tests/mail_test_helpers";
import {describe, expect, test} from "@odoo/hoot";
import {Chatter} from "@mail/chatter/web_portal/chatter";

describe.current.tags("desktop");
defineMailModels();

const archs = {
    "res.fake,false,form": `
        <form string="Fake">
            <sheet></sheet>
            <chatter/>
        </form>`,
};

describe("WebSendMessagePopup", () => {
    test("openFullComposer dispatches the full-composer wizard action", async () => {
        registerArchs(archs);
        // Capture the live Chatter instance. The module adds openFullComposer
        // to the Chatter (a new method, no core override), and routes
        // toggleComposer("message") to it — invoking it directly exercises the
        // same migration code as the production "Send message" button.
        let chatter = null;
        patchWithCleanup(Chatter.prototype, {
            setup() {
                super.setup();
                chatter = this;
            },
        });
        const pyEnv = await startServer();
        const fakeId = pyEnv["res.fake"].create({});
        mockService("action", {
            async doAction(action) {
                if (action?.res_model !== "mail.compose.message") {
                    return super.doAction(...arguments);
                }
                asyncStep("full_composer");
                expect(action.target).toBe("new");
                expect(action.context.default_model).toBe("res.fake");
                expect(action.context.default_subtype_xmlid).toBe("mail.mt_comment");
                // Asserting the dispatched action is enough.
                return Promise.resolve();
            },
        });
        await start();
        await openFormView("res.fake", fakeId);
        await contains("button", {text: "Send message"});
        await chatter.openFullComposer();
        await waitForSteps(["full_composer"]);
    });
});
