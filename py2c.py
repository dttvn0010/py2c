from compiler import Compiler
import os
import traceback

if __name__ == '__main__':
    for f in ['test.py'] :#os.listdir('test/input'):
        print('Process file:', f)
        input_file = os.path.join('test/input', f)
        output_file = os.path.join('test/output', f.replace('.py', '.c'))
        with open(input_file) as fi:
            src = fi.read()

        compiler = Compiler()
        compiler.addInput(src)
        result = compiler.cppEmit()
        
        with open(output_file, 'w') as fo:
            fo.write(result)
