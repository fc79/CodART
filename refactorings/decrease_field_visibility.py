import os

try:
    import understand
except ModuleNotFoundError:
    # Error handling
    pass

from antlr4 import *
from antlr4.TokenStreamRewriter import TokenStreamRewriter

from gen.java.JavaParser import JavaParser
from gen.javaLabeled.JavaLexer import JavaLexer
from gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener


class DecreaseFieldVisibilityRefactoringListener(JavaParserLabeledListener):
    """
    ## Introduction:

    Decrease the visibility of a field from public to protected, protected to package or package to private.

    ## Pre and Post Conditions

    ### Pre Conditions:

    1. User must enter the field's name, and the source class's name for the refactoring
       in order to decrease the target field's visibility.

    ### Post Conditions:

    No specific Post Condition

    """

    def __init__(self, common_token_stream: CommonTokenStream = None, source_class=None, field_name: str = None):
        """
        To implement ِDecrease Field Visibility refactoring based on its actors.
        Detects the required field and decreases/changes its visibility status.

        Args:
            common_token_stream (CommonTokenStream): A stream of tokens generated by parsing the main file using the ANTLR parser generator
            source_class (str): Name of the class in which the refactoring has to be done
            field_name (str): Name of the field whose visibility status has to be changed

        Returns:
            No returns

        """

        if field_name is None:
            self.field_name = ""
        else:
            self.field_name = field_name

        if source_class is None:
            self.source_class = ""
        else:
            self.source_class = source_class
        if common_token_stream is None:
            raise ValueError('common_token_stream is None')
        else:
            self.token_stream_rewriter = TokenStreamRewriter(common_token_stream)

            self.is_source_class = False
            self.detected_field = None
            self.detected_method = None
            self.TAB = "\t"
            self.NEW_LINE = "\n"
            self.code = ""
            self.tempdeclarationcode = ""

    def enterClassDeclaration(self, ctx: JavaParserLabeled.ClassDeclarationContext):
        print("Refactoring started, please wait...")
        class_identifier = ctx.IDENTIFIER().getText()
        if class_identifier == self.source_class:
            self.is_source_class = True
        else:
            self.is_source_class = False

    def exitFieldDeclaration(self, ctx: JavaParserLabeled.FieldDeclarationContext):
        if not self.is_source_class:
            return None
        grand_parent_ctx = ctx.parentCtx.parentCtx
        # field_identifier = ctx.variableDeclarators().getText().split(",")
        field_identifier = ctx.variableDeclarators().variableDeclarator(0).variableDeclaratorId().IDENTIFIER().getText()
        if self.field_name in field_identifier:
            if grand_parent_ctx.modifier() == []:
                self.token_stream_rewriter.replaceRange(
                    from_idx=ctx.typeType().start.tokenIndex,
                    to_idx=ctx.typeType().stop.tokenIndex,
                    text='public ' + ctx.typeType().getText()
                )
            elif grand_parent_ctx.modifier(0).getText() == 'private':
                self.token_stream_rewriter.replaceRange(
                    from_idx=grand_parent_ctx.modifier(0).start.tokenIndex,
                    to_idx=grand_parent_ctx.modifier(0).stop.tokenIndex,
                    text='public')
            elif grand_parent_ctx.modifier(0).getText() != 'public':
                self.token_stream_rewriter.replaceRange(
                    from_idx=grand_parent_ctx.modifier(0).start.tokenIndex,
                    to_idx=grand_parent_ctx.modifier(0).stop.tokenIndex,
                    text='public ' + grand_parent_ctx.modifier(0).getText())

        print("Finished Processing...")


if __name__ == '__main__':
    print("Decrease Field Visibility")
    udb_path = "/home/ali/Documents/compiler/Research/xerces2-j/xerces2-j.udb"
    class_name = "AttributesImpl"
    field_name = "length"
    mainfile = ""
    db = understand.open(udb_path)
    for cls in db.ents("class"):
        if (cls.simplename() == class_name):
            if cls.kindname() != "Unknown Class":
                mainfile = cls.parent().longname()

    stream = FileStream(mainfile, encoding='utf8')
    # Step 2: Create an instance of AssignmentStLexer
    lexer = JavaLexer(stream)
    # Step 3: Convert the input source into a list of tokens
    token_stream = CommonTokenStream(lexer)
    # Step 4: Create an instance of the AssignmentStParser
    parser = JavaParser(token_stream)
    parser.getTokenStream()
    parse_tree = parser.compilationUnit()
    my_listener = DecreaseFieldVisibilityRefactoringListener(common_token_stream=token_stream,
                                                             source_class=class_name,
                                                             field_name=field_name)
    walker = ParseTreeWalker()
    walker.walk(t=parse_tree, listener=my_listener)

    with open(mainfile, mode='w', newline='') as f:
        f.write(my_listener.token_stream_rewriter.getDefaultText())