# Magik Basic Nodes

Install: extract Magik_Basic_Nodes into ComfyUI/custom_nodes, restart ComfyUI, then refresh the browser. No extra dependencies.

## Magik Compare
Connect a and b. Number mode accepts numbers and numeric strings. Text mode accepts scalar values and compares text lexicographically. Contains/Starts with/Ends with test whether a contains/starts with/ends with b. Text operations are case-sensitive unless disabled. Number mode uses an absolute tolerance: numbers within tolerance count as equal, including for inclusive comparisons; strict comparisons exclude them. Outputs result and inverse.

## Magik Math
Inputs a and b can be typed or connected. Binary operations use both; unary operations use a. Round uses decimals (Python rounding: ties to even). Clamp uses minimum/maximum and accepts reversed bounds. Map range maps a from minimum…maximum to output_minimum…output_maximum, supports descending ranges, and optionally clamps to the input range. Other operations ignore range controls. FLOAT output preserves the result; INT output truncates toward zero. Invalid domains, division by zero, complex results, and nonfinite results raise readable errors.

## Magik Boolean
A toggle with value, inverse, integer (0/1), and lowercase string (false/true) outputs.

## Magik Type Convert
Select String, Integer, Float, or Boolean. The converted socket is wildcard so it can connect to the selected target type: choose a target matching the receiving input. Changing target does not rewire downstream nodes.

Integer rounding: Truncate (toward zero), Round (ties to even), Floor, Ceil. Exact integer strings preserve precision. String conversion accepts scalars and None; padding applies to integer inputs, includes the sign, and never truncates. Boolean text explicitly parses true/false, yes/no, on/off, 1/0, or empty; numeric zero is false and other finite numbers are true. Invalid conversions stop with an error. These are scalar utilities; use Magik Show Any to inspect tensors and objects.

## Magik Float
Editable float with 0.01 arrow increments. Precision (0–12) rounds the FLOAT output and formats the STRING output with fixed decimal places. Python ties-to-even rounding applies. Controls persist through normal workflow serialization.

## Magik Length
Auto: text → line count; dictionary → entries; IMAGE tensor → batch count; Python containers/ComfyUI execution lists → element count. Auto never opens files. Select Text file lines to read a local UTF-8/UTF-16/Latin-1 file by path; files are streamed. Paths refer to the ComfyUI server machine. Supports character counts and optional exclusion of blank/whitespace-only lines. Empty text is 0 lines; a final newline terminates the last line without adding an extra line. File mode follows standard text-file newline conventions (LF, CRLF, CR). Text lines additionally recognizes Python splitlines Unicode separators. Characters are Unicode code points. For a singleton execution list containing text or an image, explicitly select List elements if you want 1 rather than inspecting the contained value. ComfyUI list mapping is disabled on this node so it counts complete execution lists.

## Magik Logic
AND/OR/XOR/NOT/NAND/NOR/XNOR, with result and inverse outputs. NOT uses a only; b is ignored. Boolean widgets can be converted to connected inputs using ComfyUI's normal widget controls.

## Magik Image Info
Passes IMAGE through unchanged and outputs width, height, batch count, channels, numeric width/height ratio, reduced ratio text, megapixels per image, and a summary including dtype/device. Reads tensor metadata only, without pixel conversion or GPU synchronization. Expects the standard ComfyUI IMAGE layout [batch, height, width, channels].
