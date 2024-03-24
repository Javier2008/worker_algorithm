import typing

from common._standalone import Federation as RawFederation, Table as RawTable
from common.abc import FederationABC
from common.abc import GarbageCollectionABC
from common.common import Party, log
from common.computing.standalone import Table

LOGGER = log.getLogger()


class Federation(FederationABC):
    def __init__(self, standalone_session, federation_session_id, party):
        LOGGER.debug(
            f"[federation.standalone]init federation: "
            f"standalone_session={standalone_session}, "
            f"federation_session_id={federation_session_id}, "
            f"party={party}"
        )
        self._federation = RawFederation(
            standalone_session, federation_session_id, party
        )
        LOGGER.debug("[federation.standalone]init federation context done")

    def remote(
        self,
        v,
        name: str,
        tag: str,
        parties: typing.List[Party],
        gc: GarbageCollectionABC,
    ):
        if not _remote_tag_not_duplicate(name, tag, parties):
            raise ValueError(f"remote to {parties} with duplicate tag: {name}.{tag}")

        if isinstance(v, Table):
            # noinspection PyProtectedMember
            v = v._table
        return self._federation.remote(v=v, name=name, tag=tag, parties=parties)

    # noinspection PyProtectedMember
    def get(
        self, name: str, tag: str, parties: typing.List[Party], gc: GarbageCollectionABC
    ) -> typing.List:
        for party in parties:
            if not _get_tag_not_duplicate(name, tag, party):
                raise ValueError(f"get from {party} with duplicate tag: {name}.{tag}")

        rtn = self._federation.get(name=name, tag=tag, parties=parties)
        return [Table(r) if isinstance(r, RawTable) else r for r in rtn]

    def cleanup(self, parties):
        pass

_remote_history = set()


def _remote_tag_not_duplicate(name, tag, parties):
    for party in parties:
        if (name, tag, party) in _remote_history:
            return False
        _remote_history.add((name, tag, party))
    return True


_get_history = set()


def _get_tag_not_duplicate(name, tag, party):
    if (name, tag, party) in _get_history:
        return False
    _get_history.add((name, tag, party))
    return True
