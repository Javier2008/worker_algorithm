import typing

from algorithm.protobuf.model_migrate.converter.binning_model_converter import FeatureBinningConverter
from algorithm.protobuf.model_migrate.converter.converter_base import ProtoConverterBase
from algorithm.protobuf.model_migrate.converter.feature_selection_model_converter import \
    HeteroFeatureSelectionConverter
from algorithm.protobuf.model_migrate.converter.pearson_model_converter import HeteroPearsonConverter
from algorithm.protobuf.model_migrate.converter.tree_model_converter import HeteroSBTConverter


def converter_factory(module_name: str) -> typing.Optional[ProtoConverterBase]:
    if module_name == 'HeteroSecureBoost':
        return HeteroSBTConverter()
    elif module_name == 'HeteroFastSecureBoost':
        return HeteroSBTConverter()
    elif module_name == 'HeteroPearson':
        return HeteroPearsonConverter()
    elif module_name == 'HeteroFeatureBinning':
        return FeatureBinningConverter()
    elif module_name == 'HeteroFeatureSelection':
        return HeteroFeatureSelectionConverter()
    else:
        return None
