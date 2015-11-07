describe("Serialization functions", function() {

    var todo_model;

    beforeEach(function() {
        todo_model = new TodoModel();
    });

    it("should get text and returns an object", function() {
        var input_line = "Some todo line +todo +proj2 @home"
        expect(todo_model.serialize).toBeDefined();
        expect(todo_model.serialize(input_line).line).toBeDefined();
        expect(todo_model.serialize(input_line).line).toBe("Some todo line");
        expect(todo_model.serialize(input_line).projects).toEqual(["+todo", "+proj2"]);
        expect(todo_model.serialize(input_line).contexts).toEqual(["@home"]);
        expect(todo_model.serialize(input_line).done).toBe(false);
        expect(todo_model.serialize("x Done item").done).toBe(true);
        expect(todo_model.serialize("x Done item").line).toBe("Done item");
    });

    it("should get object make from it representative string", function() {
        expect(todo_model.unserialize).toBeDefined();
        var input_object = {
            done: false,
            line: "Some todo line",
            projects: ["+todo", "+proj2"],
            contexts: ["@home"]
        }
        expect(typeof(todo_model.unserialize(input_object))).toBe("string");
        expect(todo_model.unserialize(input_object)).toBe("Some todo line +todo +proj2 @home");
    });

});
