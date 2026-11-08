import math
from pathlib import Path

from .nodes import ANY


class MagikFloat:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'value': ('FLOAT', {'default': 0.0, 'min': -1e100, 'max': 1e100, 'step': 0.01}),
            'precision': ('INT', {'default': 3, 'min': 0, 'max': 12}),
        }}

    RETURN_TYPES = ('FLOAT', 'STRING')
    RETURN_NAMES = ('float', 'string')
    FUNCTION = 'emit'
    CATEGORY = 'Magik/Math'

    def emit(self, value, precision):
        if not math.isfinite(value):
            raise ValueError('Magik Float requires a finite value.')
        value = round(float(value), precision)
        return (value, f'{value:.{precision}f}')


def image_shape(image):
    shape = getattr(image, 'shape', None)
    if shape is None or len(shape) != 4:
        raise ValueError('Expected a ComfyUI IMAGE batch with shape [batch, height, width, channels].')
    batch, height, width, channels = map(int, shape)
    if batch < 0 or min(height, width, channels) <= 0:
        raise ValueError('Invalid image dimensions.')
    return batch, height, width, channels


class MagikLength:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'value': (ANY,),
            'mode': (['Auto', 'Text lines', 'Text characters', 'Text file lines',
                      'List elements', 'Image batch', 'Dictionary entries'],),
            'include_empty_lines': ('BOOLEAN', {'default': True}),
            'encoding': (['utf-8-sig', 'utf-8', 'utf-16', 'latin-1'],),
        }}

    # Receive ComfyUI execution lists as a whole rather than mapping over them.
    INPUT_IS_LIST = True
    RETURN_TYPES = ('INT',)
    RETURN_NAMES = ('length',)
    FUNCTION = 'measure'
    CATEGORY = 'Magik/Inspect'

    def measure(self, value, mode, include_empty_lines, encoding):
        mode, include_empty_lines, encoding = mode[0], include_empty_lines[0], encoding[0]
        # A single socket value is wrapped by ComfyUI. Multi-item execution
        # lists remain lists; a nested Python list is kept as the payload.
        payload = value[0] if len(value) == 1 else value
        if mode == 'Auto':
            if len(value) != 1:
                mode = 'List elements'
            elif isinstance(payload, str):
                mode = 'Text lines'
            elif isinstance(payload, dict):
                mode = 'Dictionary entries'
            elif hasattr(payload, 'shape') and len(payload.shape) == 4:
                mode = 'Image batch'
            elif isinstance(payload, (list, tuple, set, frozenset)):
                mode = 'List elements'
            else:
                raise ValueError('Magik Length cannot infer this datatype; select a mode.')
        if mode == 'List elements':
            if isinstance(payload, (list, tuple, set, frozenset)):
                length = len(payload)
            else:
                # A one-item ComfyUI execution list is still a valid list.
                length = len(value)
        elif mode == 'Image batch':
            length = sum(image_shape(image)[0] for image in value)
        elif mode == 'Dictionary entries':
            if not isinstance(payload, dict):
                raise ValueError('Dictionary entries requires a dictionary.')
            length = len(payload)
        elif mode in ('Text lines', 'Text characters', 'Text file lines'):
            if not isinstance(payload, str):
                raise ValueError(f'{mode} requires one string input.')
            if mode == 'Text file lines':
                # Explicit file mode only: Auto never treats text as a path.
                try:
                    with Path(payload).expanduser().open('r', encoding=encoding) as stream:
                        length = sum(1 for line in stream if include_empty_lines or line.strip())
                except (OSError, UnicodeError, ValueError) as exc:
                    raise ValueError(f'Magik Length could not read the text file: {exc}') from exc
            elif mode == 'Text characters':
                length = len(payload)
            else:
                lines = payload.splitlines()
                length = len(lines) if include_empty_lines else sum(bool(line.strip()) for line in lines)
        else:
            raise ValueError(f'Unknown length mode: {mode}')
        return (length,)


class MagikLogic:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'operation': (['AND', 'OR', 'XOR', 'NOT', 'NAND', 'NOR', 'XNOR'],),
            'a': ('BOOLEAN', {'default': False}),
            'b': ('BOOLEAN', {'default': False}),
        }}

    RETURN_TYPES = ('BOOLEAN', 'BOOLEAN')
    RETURN_NAMES = ('result', 'inverse')
    FUNCTION = 'evaluate'
    CATEGORY = 'Magik/Logic'

    def evaluate(self, operation, a, b):
        a, b = bool(a), bool(b)
        operations = {'AND': a and b, 'OR': a or b, 'XOR': a != b,
                      'NOT': not a, 'NAND': not (a and b),
                      'NOR': not (a or b), 'XNOR': a == b}
        if operation not in operations:
            raise ValueError(f'Unknown logic operation: {operation}')
        result = operations[operation]
        return (result, not result)


class MagikImageInfo:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'image': ('IMAGE',)}}

    RETURN_TYPES = ('IMAGE', 'INT', 'INT', 'INT', 'INT', 'FLOAT', 'STRING', 'FLOAT', 'STRING')
    RETURN_NAMES = ('image', 'width', 'height', 'batch_count', 'channels',
                    'aspect_ratio', 'aspect_ratio_text', 'megapixels', 'summary')
    FUNCTION = 'inspect'
    CATEGORY = 'Magik/Inspect'

    def inspect(self, image):
        batch, height, width, channels = image_shape(image)
        divisor = math.gcd(width, height)
        ratio = f'{width // divisor}:{height // divisor}'
        megapixels = width * height / 1_000_000
        summary = (f'{width} × {height} | {ratio} | {megapixels:.3f} MP per image\n'
                   f'Batch: {batch} | Channels: {channels}\n'
                   f'Dtype: {getattr(image, "dtype", "unknown")} | Device: {getattr(image, "device", "unknown")}')
        return (image, width, height, batch, channels, width / height, ratio, megapixels, summary)
