# Battlezone 98R Blender ToolKit
# Copyright (C) 2024–2025 “GrizzlyOne95” and contributors
#
# This file is part of BZ98R Blender ToolKit, which is distributed
# under the terms of the GNU General Public License v3.0.
# See the LICENSE file or <https://www.gnu.org/licenses/>.

class ModelPorterError(Exception):
    """Base class for all model porter exceptions."""
    pass

class AnimationAlreadyLoadedError(ModelPorterError):
    """Raised when an animation with the same index is already loaded."""
    pass

class InvalidBoneTypeError(ModelPorterError, ValueError):
    """Raised when an invalid bone type is specified."""
    pass

class MaterialConflictError(ModelPorterError):
    """Raised when there is a conflict in material definitions."""
    pass

class HierarchyError(ModelPorterError):
    """Raised when there is an error in the object hierarchy (e.g. circular parenting)."""
    pass

class UnsupportedFileTypeError(ModelPorterError, ValueError):
    """Raised when an unsupported file type is encountered."""
    pass

class InvalidSettingError(ModelPorterError, ValueError):
    """Raised when an invalid setting is provided."""
    pass

class POVNotFoundError(ModelPorterError):
    """Raised when a POV bone is expected but not found."""
    pass
