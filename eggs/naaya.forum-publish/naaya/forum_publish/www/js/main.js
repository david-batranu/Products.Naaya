(function(B, _, rangy) {

    "use strict";

    /* B => Backbone */
    // regular expression that replaces multiple spaces with one space
    var matchSpaces = /\s{2,}/g;

    var isForumPage = function () { return $(".forum_topic").length > 0; };
    var sidebarExists = function () { return $("#sidebar-port").length > 0};

    // Dictionary that will contain all text translated in user language
    var translation_dictonary = {};

    var gettext = function (msg) {
        return translation_dictonary[msg] || msg;
    };

    // dispatcher that will handle custom events
    var dispatcher = _.clone(B.Events);

    var MessageModel = B.Model.extend({
        defaults: { content: null, author: null }
    });

    var PublishButtonView = B.View.extend({
        /* View that handles the render for the publish button. */
        tagName: "a",

        className: "btn-publish",

        selector: ".message_top_buttons, .message_top_buttons2",

        initialize: function () { this.render(); },

        render: function () {
            this.$el.text(gettext("Publish")); // how can we do i18n
            $(this.selector).append(this.$el);
        }
    });

    var BoardView = B.View.extend({
        /* Renders the publish button and adds the events for publishing a
           selected text. */
        el: "#middle_port",

        events: { "mousedown .btn-publish": "publish" },

        dialogOptions: {
            modal: true,
            buttons: {
                Ok: function() { $(this).dialog("close"); }
            }
        },

        initialize: function () {
            this.getTranslation(this.render);
            dispatcher.on("publish/message", this.publishMessage, this);
        },

        render: function () {
            new PublishButtonView();
        },

        publish: function (e) {
            e.preventDefault();
            // fetch selected text with html tags
            var selection = rangy.getSelection();
            var message = $.trim(selection.toHtml().replace(matchSpaces, " "));
            var author = $(e.currentTarget)
                .parents(".forum_topic, .forum_message")
                .find(".forum_topic_author, .forum_message_author").text();
            author = $.trim(author.replace(matchSpaces, " "));

            if(!$.trim(message)) {
                this.notice(gettext("Please select a range"));
                return;
            }
            if(!this._checkIfSelectionInContainer(e, selection)) {
                this.notice(gettext("Please select a range in the same container"));
                return;
            }

            dispatcher.trigger("publish/message", message, author);
        },

        _checkIfSelectionInContainer: function(e, selection) {
            /* Check to see if selected text is in the same container with
               publish button */
            var anchorN = $(selection.anchorNode)
                .parents(".forum_topic, .forum_message")[0];
            var focusN = $(selection.focusNode)
                .parents(".forum_topic, .forum_message")[0];
            var parents = $(e.currentTarget)
                .parents(".forum_topic, .forum_message")[0];
            return (parents === anchorN) && (parents === focusN);
        },

        notice: function(message) {
            /* Creates an jquery UI dialog and displays a message. */
            var dialog = this.make("div", {title: gettext("Alert")}, message);
            $(dialog).dialog(this.dialogOptions);
        },

        publishMessage: function(message, author) {
            var model = new MessageModel({ content: message, author: author });
            if(!sidebarExists()) {
                this.$el.addClass("sidebar-fix", "fast");
                new SidebarView();
            }
            new MessageView({ model: model });
        },

        getTranslation: function (callback) {
            /* Get i18n translation and after render the view */
            var url = $("base").attr("href") + "../forum_publish_translations";
            $.get(url, function (data) {
                translation_dictonary = data;
                $.isFunction(callback) && callback();
            }, "json");
        }
    });

    var SidebarView = B.View.extend({
        /* Renders a sidebar if it doesn't exist with default content. */
        id: "sidebar-port",

        selector: "#middle_port",

        className: "sidebar",

        events: {
            "click .publish": "publish",
            "click .cancel": "cancel"
        },

        initialize: function () {
            this.render();
            // bind custom event for checking id sidebar is empty
            dispatcher.on("message/remove", this.checkIfSidebarEmpty, this);
        },

        render: function () {
            var publishButtons = this._renderPublishButtons();
            var self = this;

            this.$el.hide();
            this.$el.html(this.make("p", { class: "empty" },
                gettext("No published text")
            ));
            this.$el.append(publishButtons);

            $(this.selector).after(this.$el);
            this.$el.delay(100).effect("slide", { direction: "right" }, "fast");
        },

        _renderPublishButtons: function () {
            var publishButtons = this.make("div", { class: "publish-buttons"});
            $(publishButtons)
                .append(this.make("a", { class: "publish"}, gettext("Publish")))
                .append(this.make("a", { class: "cancel"}, gettext("Cancel")));
            return publishButtons;
        },

        checkIfSidebarEmpty: function () {
            /* Checks if any message_published div exists in sidebar */
            var $empty = this.$el.find(".empty");
            var $publish = this.$el.find(".publish");

            if(this.$el.find(".message-published").length == 0) {
                $empty.show();
                $publish.hide();
            } else {
                $empty.hide()
                $publish.show();
            }
        },

        publish: function (e) {
            /* Serialize and publish form */
            var form = this.$el.find(":input");
            var url = $("base").attr("href") + "../forum_publish_save";

            $.post(url, form.serialize(), function(data) {
                if(data.status == "success") {
                    document.location = data.url;
                }
            }, "json");
        },

        cancel: function () {
            this.$el.effect("slide", { direction: "right", mode: "hide" },
                "fast", function () { $(this).remove();   });
            $(this.selector).delay(100).removeClass("sidebar-fix", "fast");
        }
    });

    var MessageView = B.View.extend({
        /* Renders a published message and bind events for it */
        className: "message-published",

        selector: "#sidebar-port",

        events: {
            "mouseover": "toggleRemove",
            "mouseout": "toggleRemove",
            "click .remove": "remove"
        },

        initialize: function () {
            this.author = this.options.author;
            this.render();
            dispatcher.trigger("message/remove");
        },

        render: function () {
            var content = this.model.get("content");
            var author = this.model.get("author");

            var messageHtml = this.make("textarea",
                { readonly: "readonly", rows: 5, cols: 5, name: "content" },
                content);
            var authorHtml = this.make("input",
                { type: "hidden", value: author, name: "author" });

            this.$el.append(messageHtml).append(authorHtml);
            $(this.selector).find(".publish-buttons").before(this.$el);
        },

        toggleRemove: function (e) {
            var $remove = $(e.currentTarget).find(".remove");
            if($remove.length > 0) {
                $remove.toggle();
            } else {
                this.$el.append(this.make("a", { class: "remove" }, gettext("Remove")));
            }
        },

        remove: function () {
            this.$el.slideUp("fast", function () {
                $(this).remove();
                dispatcher.trigger("message/remove");
            });
        }
    });

    $(function () {
        // only do the magic if on a forum page
        isForumPage() && new BoardView();
    });

}(Backbone, _, rangy));