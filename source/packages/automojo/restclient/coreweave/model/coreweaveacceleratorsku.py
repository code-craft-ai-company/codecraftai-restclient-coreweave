"""
    .. module:: coreweaveacceleratorsku
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Hand-authored :class:`CoreweaveAcceleratorSku` data model.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional


class CoreweaveAcceleratorSku:
    """
        Typed record describing a GPU SKU available in a CoreWeave project.
    """

    def __init__(self, *, name: str, gpu_model: str, memory_gb: int,
                 available_regions: Optional[List[str]] = None) -> None:
        """
            Initialize a :class:`CoreweaveAcceleratorSku`.

            :param name: The catalog SKU name.
            :param gpu_model: The GPU model identifier.
            :param memory_gb: The per-GPU memory in gigabytes.
            :param available_regions: The regions the SKU is offered in.

            :returns: ``None``.
        """
        self.name = name
        self.gpu_model = gpu_model
        self.memory_gb = memory_gb
        self.available_regions = available_regions if available_regions is not None else []
        return

    @classmethod
    def from_payload(cls, *, payload: Dict[str, Any]) -> "CoreweaveAcceleratorSku":
        """
            Build a :class:`CoreweaveAcceleratorSku` from an API payload dict.

            :param payload: The decoded API object.

            :returns: A populated :class:`CoreweaveAcceleratorSku`.
        """
        name = payload.get("name", "")
        gpu_model = payload.get("gpu_model", "")
        memory_gb = payload.get("memory_gb", 0)
        available_regions = payload.get("available_regions", None)

        rtnval = cls(name=name, gpu_model=gpu_model, memory_gb=memory_gb,
                     available_regions=available_regions)
        return rtnval


__all__ = ["CoreweaveAcceleratorSku"]
