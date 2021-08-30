import glob
import hashlib
import random
from pathlib import Path
from typing import Any, List

from PIL import Image
from injector import singleton, inject

from common.concurrency import cpu_bound_task
from config import cfg


@singleton
class AvatarService:
    @inject
    def __init__(self):
        self._avatar_images_path = Path(cfg.avatar_data_folder)
        self._avatar_images_path.mkdir(exist_ok=True, parents=True)
        self._bodies = self._get_layers_paths("bodies")
        self._accessories = self._get_layers_paths("accessories")
        self._glasses = self._get_layers_paths("glasses")
        self._hats = self._get_layers_paths("hats")

    async def generate_and_save_avatar(self, identifier: str, filename: str) \
            -> None:
        await cpu_bound_task(
            self._generate_and_save_avatar, identifier, filename)

    async def generate_avatar(self, identifier: str) -> Any:
        return await cpu_bound_task(self._generate_avatar, identifier)

    def _generate_and_save_avatar(self, identifier: str, filename: str) -> None:
        avatar_image = self._generate_avatar(identifier)
        avatar_image.save(
            self._avatar_images_path / f"{filename}.png",
            "PNG",
            optimize=True)

    def _generate_avatar(self, identifier: str) -> Any:
        identifier_hash = int(hashlib.md5(str(identifier).encode()).hexdigest(),
                              base=16)
        random.seed(identifier_hash)
        layer0 = self._bodies[random.randint(0, len(self._bodies) - 1)]
        layer1 = self._accessories[
            random.randint(0, len(self._accessories) - 1)]
        layer2 = self._glasses[random.randint(0, len(self._glasses) - 1)]
        layer3 = self._hats[random.randint(0, len(self._hats) - 1)]
        avatar = Image.alpha_composite(Image.open(layer0), Image.open(layer1))
        avatar = Image.alpha_composite(avatar, Image.open(layer2))
        avatar = Image.alpha_composite(avatar, Image.open(layer3))
        return avatar

    def _get_layers_paths(self, layer_type: str) -> List[str]:
        paths = glob.glob(f"avatar/images/{layer_type}/*")
        paths.sort()
        return paths
