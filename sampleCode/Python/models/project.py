"""Projects and folders: how analyses are organized.

A Project is the container for one analysis. It fixes the Aggregation Scheme and
Household Set at creation, and everything inside it, every Event and every Group,
has to be consistent with that choice.

Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects
"""

import dataclasses
import uuid

from utilities.json_helper import ApiModel


@dataclasses.dataclass(kw_only=True)
class Project(ApiModel):
    """One impact analysis project.

    Leave `id` unset when creating; the API generates it and returns it. `title`
    must be unique for your account and must avoid an ampersand and the characters
    `| ; % * ? ! = ' " ^ #`.

    `aggregation_scheme_id` and `household_set_id` cannot be changed afterwards,
    and the household set has to be one of the scheme's `household_set_ids`.

    `last_impact_run_id` is filled in after the project has been run, and is the
    run whose results you read.
    """

    title: str = ""
    aggregation_scheme_id: int = 0
    household_set_id: int = 0
    id: uuid.UUID | str | None = None

    # Multi-regional input-output analysis, which traces effects between the
    # project's regions instead of treating each in isolation. See the MrioProject
    # workflow.
    is_mrio: bool = False

    # The folder this project sits in, or None for the top level.
    folder_id: int | None = None

    last_impact_run_id: int | None = None

    def describe(self) -> str:
        """One line naming the project, for the console."""
        return f"{self.title}  id={self.id}"


@dataclasses.dataclass(kw_only=True)
class Folder(ApiModel):
    """A folder in IMPLAN Cloud, used to keep a batch of projects together.

    Note the type of `id`. A folder reports its own id as a string, while
    `Project.folder_id` and a folder's own `parent_id` refer to the same value as an
    integer. The string is canonical, so `folder_id_for_project` does the
    conversion in one place rather than leaving it to every caller.
    """

    title: str = ""
    id: str | None = None
    parent_id: int | None = None

    @property
    def folder_id_for_project(self) -> int | None:
        """This folder's id in the integer form `Project.folder_id` expects."""
        return None if self.id is None else int(self.id)
