import math
import operator


class AnyType(str):
    def __ne__(self, other):
        return False


ANY = AnyType('*')
NUMBER = ('FLOAT', {'default': 0.0, 'min': -1e100, 'max': 1e100, 'step': 0.1})


def number(value):
    if not isinstance(value, (str, int, float, bool)):
        raise ValueError(f'Expected a number or numeric text, got {type(value).__name__}.')
    try:
        result = float(value.strip() if isinstance(value, str) else value)
    except (ValueError, OverflowError) as exc:
        raise ValueError(f'Cannot convert {value!r} to a finite number.') from exc
    if not math.isfinite(result):
        raise ValueError('NaN and infinity are not supported.')
    return result


class MagikCompare:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'a': (ANY,), 'b': (ANY,),
            'mode': (['Number', 'Text'],),
            'operation': (['Equal', 'Not equal', 'Less than', 'Less or equal',
                           'Greater than', 'Greater or equal', 'Contains',
                           'Starts with', 'Ends with'],),
            'case_sensitive': ('BOOLEAN', {'default': True}),
            'tolerance': ('FLOAT', {'default': 0.0, 'min': 0.0, 'max': 1e100}),
        }}

    RETURN_TYPES = ('BOOLEAN', 'BOOLEAN')
    RETURN_NAMES = ('result', 'inverse')
    FUNCTION = 'compare'
    CATEGORY = 'Magik/Logic'

    def compare(self, a, b, mode, operation, case_sensitive=True, tolerance=0.0):
        if mode == 'Number':
            a, b = number(a), number(b)
            tolerance = number(tolerance)
            if tolerance < 0:
                raise ValueError('Tolerance must be nonnegative.')
            equal = abs(a - b) <= tolerance
            operations = {
                'Equal': lambda: equal, 'Not equal': lambda: not equal,
                'Less than': lambda: a < b and not equal,
                'Less or equal': lambda: a < b or equal,
                'Greater than': lambda: a > b and not equal,
                'Greater or equal': lambda: a > b or equal,
            }
        elif mode == 'Text':
            if not isinstance(a, (str, int, float, bool)) or not isinstance(b, (str, int, float, bool)):
                raise ValueError('Text comparison accepts strings and scalar numbers/booleans.')
            a, b = str(a), str(b)
            if not case_sensitive:
                a, b = a.casefold(), b.casefold()
            operations = {
                'Equal': lambda: a == b, 'Not equal': lambda: a != b,
                'Less than': lambda: a < b, 'Less or equal': lambda: a <= b,
                'Greater than': lambda: a > b, 'Greater or equal': lambda: a >= b,
                'Contains': lambda: b in a,
                'Starts with': lambda: a.startswith(b), 'Ends with': lambda: a.endswith(b),
            }
        else:
            raise ValueError(f'Unknown comparison mode: {mode}')
        if operation not in operations:
            raise ValueError(f'{operation} is unavailable in {mode} mode.')
        result = bool(operations[operation]())
        return (result, not result)


class MagikMath:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'operation': (['Add', 'Subtract', 'Multiply', 'Divide', 'Floor divide',
                           'Modulo', 'Power', 'Minimum', 'Maximum', 'Average',
                           'Absolute', 'Negate', 'Square root', 'Round', 'Floor',
                           'Ceil', 'Clamp', 'Map range'],),
            'a': NUMBER, 'b': NUMBER,
            'minimum': ('FLOAT', {'default': 0.0, 'min': -1e100, 'max': 1e100}),
            'maximum': ('FLOAT', {'default': 1.0, 'min': -1e100, 'max': 1e100}),
            'output_minimum': ('FLOAT', {'default': 0.0, 'min': -1e100, 'max': 1e100}),
            'output_maximum': ('FLOAT', {'default': 100.0, 'min': -1e100, 'max': 1e100}),
            'decimals': ('INT', {'default': 0, 'min': 0, 'max': 12}),
            'clamp_mapping': ('BOOLEAN', {'default': True}),
        }}

    RETURN_TYPES = ('FLOAT', 'INT')
    RETURN_NAMES = ('float', 'int')
    FUNCTION = 'calculate'
    CATEGORY = 'Magik/Math'

    def calculate(self, operation, a, b, minimum=0.0, maximum=1.0,
                  output_minimum=0.0, output_maximum=100.0, decimals=0,
                  clamp_mapping=True):
        a, b = number(a), number(b)
        binary = {'Add': operator.add, 'Subtract': operator.sub,
                  'Multiply': operator.mul, 'Divide': operator.truediv,
                  'Floor divide': operator.floordiv, 'Modulo': operator.mod,
                  'Power': operator.pow, 'Minimum': min, 'Maximum': max,
                  'Average': lambda x, y: x / 2 + y / 2}
        unary = {'Absolute': abs, 'Negate': operator.neg,
                 'Square root': math.sqrt, 'Round': lambda x: round(x, decimals),
                 'Floor': math.floor, 'Ceil': math.ceil}
        try:
            if operation in binary:
                value = binary[operation](a, b)
            elif operation in unary:
                value = unary[operation](a)
            elif operation == 'Clamp':
                lo, hi = sorted((number(minimum), number(maximum)))
                value = max(lo, min(hi, a))
            elif operation == 'Map range':
                lo, hi = number(minimum), number(maximum)
                if lo == hi:
                    raise ValueError('Map range requires different input bounds.')
                ratio = (a - lo) / (hi - lo)
                if clamp_mapping:
                    ratio = max(0.0, min(1.0, ratio))
                value = number(output_minimum) + ratio * (number(output_maximum) - number(output_minimum))
            else:
                raise ValueError(f'Unknown operation: {operation}')
            value = number(value)
        except (ZeroDivisionError, OverflowError, ValueError, TypeError) as exc:
            raise ValueError(f'Magik Math — {operation}: {exc}') from exc
        return (value, int(value))


class MagikBoolean:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'value': ('BOOLEAN', {'default': False})}}

    RETURN_TYPES = ('BOOLEAN', 'BOOLEAN', 'INT', 'STRING')
    RETURN_NAMES = ('value', 'inverse', 'int', 'string')
    FUNCTION = 'emit'
    CATEGORY = 'Magik/Logic'

    def emit(self, value):
        value = bool(value)
        return (value, not value, int(value), 'true' if value else 'false')


class MagikTypeConvert:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'value': (ANY,),
            'target': (['String', 'Integer', 'Float', 'Boolean'],),
            'integer_rounding': (['Truncate', 'Round', 'Floor', 'Ceil'],),
            'padding': ('INT', {'default': 1, 'min': 1, 'max': 99}),
        }}

    RETURN_TYPES = (ANY,)
    RETURN_NAMES = ('converted',)
    FUNCTION = 'convert'
    CATEGORY = 'Magik/Convert'

    def convert(self, value, target, integer_rounding='Truncate', padding=1):
        if target == 'String':
            if not isinstance(value, (str, int, float, bool, type(None))):
                raise ValueError('String conversion accepts scalar values only; use Magik Show Any for objects.')
            if isinstance(value, bool):
                result = 'true' if value else 'false'
            else:
                result = str(value)
            if isinstance(value, int) and not isinstance(value, bool):
                result = result.zfill(padding)
        elif target == 'Integer':
            if isinstance(value, (int, bool)):
                result = int(value)
            elif isinstance(value, str) and value.strip().lstrip('+-').isascii() and value.strip().lstrip('+-').isdigit():
                result = int(value.strip())
            else:
                rounding = {'Truncate': int, 'Round': round, 'Floor': math.floor, 'Ceil': math.ceil}
                if integer_rounding not in rounding:
                    raise ValueError(f'Unknown rounding mode: {integer_rounding}')
                result = int(rounding[integer_rounding](number(value)))
        elif target == 'Float':
            result = number(value)
        elif target == 'Boolean':
            if isinstance(value, bool):
                result = value
            elif isinstance(value, (int, float)):
                result = number(value) != 0
            elif isinstance(value, str):
                text = value.strip().casefold()
                if text in ('true', 'yes', 'on', '1'):
                    result = True
                elif text in ('false', 'no', 'off', '0', ''):
                    result = False
                else:
                    raise ValueError('Boolean text must be true/false, yes/no, on/off, 1/0, or empty.')
            else:
                raise ValueError(f'Cannot convert {type(value).__name__} to Boolean.')
        else:
            raise ValueError(f'Unknown target: {target}')
        return (result,)
