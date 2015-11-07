TodoModel = Backbone.Model.extend({
    defaults: {
        line: '',
        done: false,
        projects: [],
        contexts: []
    },
    toJSON: function() {
        var json = Backbone.Model.prototype.toJSON.apply(this, arguments);
        json.cid = this.cid;
        return json;
    },
    serialize: function(line) {
        var result = {
            line: '',
            done: false,
            projects: [],
            contexts: []
        };
        var line_words = [];
        if (line.startsWith("x ")) {
            result.done = true;
            line = line.slice(2);
        }
        _.each(line.split(" "), function(word) {
            if (word.startsWith('+')) {
                result.projects.push(word);
            } else if (word.startsWith('@')) {
                result.contexts.push(word);
            } else {
                line_words.push(word);
            }
        });
        result.line = line_words.join(" ");
        return result;
    },
    unserialize: function(obj) {
        var line = [];
        if (obj.done) {
            line.push("x");
        }
        line.push(obj.line);
        line = line.concat(obj.projects);
        line = line.concat(obj.contexts);
        return line.join(" ");
    }
});

TodoCollection = Backbone.Collection.extend({
    url: '/todo/',
    model: TodoModel
});

TodoItemView = Backbone.Marionette.ItemView.extend({
    template: '#todo-item',
    model: TodoModel,
    tagName: 'tr',
    className: 'todotxt__item',
    ui: {
        checkbox: '.js-checkbox'
    },
    events: {
        'change .js-checkbox': "recordTicked"
    },
    recordTicked: function(e) {
        var done = this.ui.checkbox.hasClass('is-checked');
        this.model.set('done', done);
        this.$el.toggleClass('js-done');
    },
    onRender: function() {
        componentHandler.upgradeElements(this.el);
        if (this.model.get('done')) {
            this.$el.addClass('js-done');
        }
    }
});

TodoEditItemView = Backbone.Marionette.ItemView.extend({
    template: '#todo-edit',
    model: TodoModel,
    className: "todotxt__edit",
    ui: {
        edit_box: '.edit_box'
    },
    events: {
        'click .js-save-item-button': "saveItem"
    },
    saveItem: function(e) {
        this.model.set('line', this.ui.edit_box.val());
        TodoTxtApp.vent.trigger('todo:new', this.model);
        this.remove();
    }
});

TodoCompositeView = Backbone.Marionette.CompositeView.extend({
    template: '#todo-list',
    tagName: 'table',
    collection: TodoCollection,
    childView: TodoItemView,
    childViewContainer: 'tbody',
    className: "todotxt__list mdl-data-table mdl-js-data-table",
    initialize: function(options) {
        var self = this;
        TodoTxtApp.vent.on('todo:save', function(e) {
            self.saveTodo(e);
        });
        TodoTxtApp.vent.on('todo:add', function(e) {
            self.addTask(e);
        });
        TodoTxtApp.vent.on('todo:new', function(model) {
            self.collection.add(model);
            self.saveTodo();
        });
    },
    saveTodo: function(e) {
        var self = this;
        self.collection.sync('create', self.collection);
    },
    addTask: function(e, model) {
        var self = this;
        if (!model) {
            model = new TodoModel();
        }
        var edit_view = new TodoEditItemView({model: model});
        TodoTxtApp.editRegion.show(edit_view);
    }
});

