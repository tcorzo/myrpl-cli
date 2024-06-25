from pycdc import decompyle

class Decompiler:
    def __init__(self, bytecode_file):
        self.bytecode_file = bytecode_file

    def decompile(self, output_file):
        try:
            with open(self.bytecode_file, 'rb') as f:
                bytecode = f.read()

            decompiled_code = decompyle(bytecode)

            with open(output_file, 'w') as f:
                f.write(decompiled_code)

            print(f"Decompiled code written to {output_file}")
        except Exception as e:
            print(f"Error decompiling: {str(e)}")
