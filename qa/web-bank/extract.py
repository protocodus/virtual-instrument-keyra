"""Extract audited Binaryen blocks without changing the generated arithmetic."""
import hashlib
from pathlib import Path
import re
import sys
from textwrap import dedent, indent

def extract(code, mode):
    if hashlib.sha256(code.encode()).hexdigest() != "b98ef68895943fa0532f3c647a31f938f73c151e73f8cd8bdbf3a8ddb13b92f2":
        raise ValueError("Unexpected scalar JavaScript artifact")
    lines = code.splitlines()
    render = " function $59($0_1) {"
    assert lines[22129] == render
    variables = lines[22131].removeprefix("  var ").removesuffix(";").split(", ")
    helpers = []
    typed = "asm" in mode
    def outline(text, name, arguments, result=None):
        used = set(re.findall(r"\$\d+(?:_1)?\b", text)).difference(arguments)
        locals_ = [v for v in variables if v.partition(" = ")[0] in used]
        body = indent(dedent(text), "  ")
        if typed and name == "renderOpenString":
            body = re.sub(r"HEAPF32\[[^\[\]\n]+\](?!\s*=)", r"Math_fround(\g<0>)", body)
            body = body.replace("4e3", "4000")
        # Float parameters keep their f32 values at the JS boundary.
        params = ", ".join(arguments)
        annotations = ""
        if typed and name == "renderOpenString":
            for arg in arguments:
                expr = f"Math_fround({arg})" if arg in ("$83_1", "$103_1") else f"{arg}|0"
                annotations += f"  {arg} = {expr};\n"
        helper = f" function {name}({params}) {{\n{annotations}  var {', '.join(locals_)};\n{body}\n"
        if result:
            helper += f"  return +{result};\n"
        helper += " }\n"
        call = f"{name}({params})"
        if typed and name == "renderOpenString":
            return helper, f"{result} = Math_fround({call});"
        return helper, (f"{result} = {call};" if result else call + ";")

    full = "\n".join(lines[25097:25442])
    inner = "\n".join(lines[25207:25398])
    outer = full
    if mode != "outer":
        args = "$0_1 $103_1 $23_1 $35_1 $8_1 $13_1 $26_1 $100_1 $22_1 $101_1 $17_1 $10_1 $24_1 $83_1 $16_1".split()
        helper, call = outline(inner, "renderOpenString", args, "$87_1")
        outer = full.replace(inner, "         " + call)
        if typed:
            factory = '''function sympatheticKernel(stdlib, foreign, heap) {
 "use asm";
 var HEAPF32 = new stdlib.Float32Array(heap);
 var Math_fround = stdlib.Math.fround;
''' + helper + " return { renderOpenString: renderOpenString };\n}\n"
            code = code.replace("function asmFunc(imports)", factory + "function asmFunc(imports)")
            heap = " var buffer = new ArrayBuffer(67108864);"
            code = code.replace(heap,heap + "\n var renderOpenString = sympatheticKernel(globalThis, {}, buffer).renderOpenString;")
        else:
            helpers.append(helper)
    if mode != "inner":
        helper, call = outline(outer, "renderSympatheticStrings", ["$6_1", "$59_1", "$13_1", "$0_1"])
        helpers.append(helper)
        outer = "       " + call
    code = code.replace(full, outer)
    return code.replace(render, "\n".join(helpers) + "\n" + render)

if __name__ == "__main__":
    mode, source, dest = sys.argv[1:]
    Path(dest).write_text(extract(Path(source).read_text(), mode))
