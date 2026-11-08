from .nodes import MagikCompare, MagikMath, MagikBoolean, MagikTypeConvert

NODE_CLASS_MAPPINGS = {
    'MagikCompare': MagikCompare,
    'MagikMath': MagikMath,
    'MagikBoolean': MagikBoolean,
    'MagikTypeConvert': MagikTypeConvert,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    'MagikCompare': 'Magik Compare',
    'MagikMath': 'Magik Math',
    'MagikBoolean': 'Magik Boolean',
    'MagikTypeConvert': 'Magik Type Convert',
}

from .extra_nodes import MagikFloat, MagikLength, MagikLogic, MagikImageInfo

NODE_CLASS_MAPPINGS.update({
    'MagikFloat': MagikFloat,
    'MagikLength': MagikLength,
    'MagikLogic': MagikLogic,
    'MagikImageInfo': MagikImageInfo,
})
NODE_DISPLAY_NAME_MAPPINGS.update({
    'MagikFloat': 'Magik Float',
    'MagikLength': 'Magik Length',
    'MagikLogic': 'Magik Logic',
    'MagikImageInfo': 'Magik Image Info',
})
