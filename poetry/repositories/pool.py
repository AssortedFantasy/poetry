from typing import List
from typing import Union

import poetry.packages

from .base_repository import BaseRepository
from .repository import Repository


class Pool(BaseRepository):
    def __init__(self, repositories=None):  # type: (Union[list, None]) -> None
        if repositories is None:
            repositories = []

        self._repositories = []

        for repository in repositories:
            self.add_repository(repository)

        super(Pool, self).__init__()

    @property
    def repositories(self):  # type: () -> List[Repository]
        return self._repositories

    def add_repository(self, repository):  # type: (Repository) -> Pool
        """
        Adds a repository to the pool.
        """
        self._repositories.append(repository)

        return self

    def remove_repository(self, repository_name):  # type: (str) -> Pool
        for i, repository in enumerate(self._repositories):
            if repository.name == repository_name:
                del self._repositories[i]

                break

        return self

    def configure(self, source):  # type: (dict) -> Pool
        """
        Configures a repository based on a source
        specification and add it to the pool.
        """
        from .legacy_repository import LegacyRepository

        if "url" in source:
            # PyPI-like repository
            if "name" not in source:
                raise RuntimeError("Missing [name] in source.")

            repository = LegacyRepository(source["name"], source["url"])
        else:
            raise RuntimeError("Unsupported source specified")

        return self.add_repository(repository)

    def has_package(self, package):
        raise NotImplementedError()

    def package(self, name, version, extras=None):
        for repository in self._repositories:
            try:
                package = repository.package(name, version, extras=extras)
            except ValueError:
                continue

            if package:
                self._packages.append(package)

                return package

        return None

    def find_packages(
        self, name, constraint=None, extras=None, allow_prereleases=False
    ):
        for repository in self._repositories:
            packages = repository.find_packages(
                name, constraint, extras=extras, allow_prereleases=allow_prereleases
            )
            if packages:
                return packages

        return []

    def search(self, query, mode=BaseRepository.SEARCH_FULLTEXT):
        from .legacy_repository import LegacyRepository

        results = []
        for repository in self._repositories:
            if isinstance(repository, LegacyRepository):
                continue

            results += repository.search(query, mode=mode)

        return results
