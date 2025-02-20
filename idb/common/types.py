#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.

import asyncio
from abc import ABCMeta
from enum import Enum
from io import StringIO
from typing import (
    IO,
    AsyncIterable,
    AsyncIterator,
    Dict,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Union,
)


LoggingMetadata = Dict[str, Optional[Union[str, List[str], int, float]]]


class Address(NamedTuple):
    host: str
    port: int


class AppProcessState(Enum):
    UNKNOWN = 0
    NOT_RUNNING = 1
    RUNNING = 2


class InstalledAppInfo(NamedTuple):
    bundle_id: str
    name: str
    architectures: Set[str]
    install_type: str
    process_state: AppProcessState
    debuggable: bool


class InstrumentsTimings(NamedTuple):
    launch_error_timeout: Optional[float] = None
    launch_retry_timeout: Optional[float] = None
    terminate_timeout: Optional[float] = None
    operation_duration: Optional[float] = None


class HIDButtonType(Enum):
    APPLE_PAY = 1
    HOME = 2
    LOCK = 3
    SIDE_BUTTON = 4
    SIRI = 5


ConnectionDestination = Union[str, Address]


class CompanionInfo(NamedTuple):
    udid: str
    host: str
    port: int
    is_local: bool

    def __eq__(self, other) -> bool:  # pyre-ignore
        return (
            self.udid == other.udid
            and self.host == other.host
            and self.port == other.port
            and self.is_local == other.is_local
        )


class ScreenDimensions(NamedTuple):
    width: int
    height: int
    density: Optional[float]
    width_points: Optional[int]
    height_points: Optional[int]


class TargetDescription(NamedTuple):
    udid: str
    name: str
    state: Optional[str]
    target_type: Optional[str]
    os_version: Optional[str]
    architecture: Optional[str]
    companion_info: Optional[CompanionInfo]
    screen_dimensions: Optional[ScreenDimensions]


class DaemonInfo(NamedTuple):
    host: str
    port: int
    targets: List[TargetDescription]


ConnectResponse = Union[CompanionInfo, DaemonInfo]


class FileEntryInfo(NamedTuple):
    path: str


class IdbException(Exception):
    pass


class AccessibilityInfo(NamedTuple):
    json: Optional[str]


class CrashLogInfo(NamedTuple):
    name: Optional[str]
    bundle_id: Optional[str]
    process_name: Optional[str]
    parent_process_name: Optional[str]
    process_identifier: Optional[int]
    parent_process_identifier: Optional[int]
    timestamp: Optional[int]


class CrashLog(NamedTuple):
    info: Optional[CrashLogInfo]
    contents: Optional[str]


class CrashLogQuery(NamedTuple):
    since: Optional[int] = None
    before: Optional[int] = None
    bundle_id: Optional[str] = None
    name: Optional[str] = None


class TestRunFailureInfo(NamedTuple):
    message: str
    file: str
    line: int


class TestActivity(NamedTuple):
    title: str
    duration: float
    uuid: str


class TestRunInfo(NamedTuple):
    bundle_name: str
    class_name: str
    method_name: str
    logs: List[str]
    duration: float
    passed: bool
    failure_info: Optional[TestRunFailureInfo]
    activityLogs: Optional[List[TestActivity]]
    crashed: bool


class InstalledTestInfo(NamedTuple):
    bundle_id: str
    name: Optional[str]
    architectures: Optional[Set[str]]


class HIDDirection(Enum):
    DOWN = 0
    UP = 1


class Point(NamedTuple):
    x: float
    y: float


class HIDTouch(NamedTuple):
    point: Point


class HIDButton(NamedTuple):
    button: HIDButtonType


class HIDKey(NamedTuple):
    keycode: int


HIDPressAction = Union[HIDTouch, HIDButton, HIDKey]


class HIDPress(NamedTuple):
    action: HIDPressAction
    direction: HIDDirection


class HIDSwipe(NamedTuple):
    start: Point
    end: Point
    delta: Optional[float]


class HIDDelay(NamedTuple):
    duration: float


HIDEvent = Union[HIDPress, HIDSwipe, HIDDelay]


class InstalledArtifact(NamedTuple):
    name: str
    uuid: Optional[str]
    progress: Optional[float]


class IdbClient:
    async def list_apps(self) -> List[InstalledAppInfo]:
        pass

    async def launch(
        self,
        bundle_id: str,
        env: Optional[Dict[str, str]] = None,
        args: Optional[List[str]] = None,
        foreground_if_running: bool = False,
        stop: Optional[asyncio.Event] = None,
    ) -> None:
        pass

    async def run_xctest(
        self,
        test_bundle_id: str,
        app_bundle_id: str,
        test_host_app_bundle_id: Optional[str] = None,
        is_ui_test: bool = False,
        is_logic_test: bool = False,
        tests_to_run: Optional[Set[str]] = None,
        tests_to_skip: Optional[Set[str]] = None,
        env: Optional[Dict[str, str]] = None,
        args: Optional[List[str]] = None,
        result_bundle_path: Optional[str] = None,
        idb_log_buffer: Optional[StringIO] = None,
        timeout: Optional[int] = None,
        poll_interval_sec: float = 0.5,
    ) -> AsyncIterator[TestRunInfo]:
        yield

    async def install(
        self, bundle: Union[str, IO[bytes]]
    ) -> AsyncIterator[InstalledArtifact]:
        yield

    async def install_dylib(
        self, dylib: Union[str, IO[bytes]]
    ) -> AsyncIterator[InstalledArtifact]:
        yield

    async def install_dsym(
        self, dsym: Union[str, IO[bytes]]
    ) -> AsyncIterator[InstalledArtifact]:
        yield

    async def install_xctest(
        self, xctest: Union[str, IO[bytes]]
    ) -> AsyncIterator[InstalledArtifact]:
        yield

    async def install_framework(
        self, framework_path: Union[str, IO[bytes]]
    ) -> AsyncIterator[InstalledArtifact]:
        yield

    async def uninstall(self, bundle_id: str) -> None:
        pass

    async def connect(
        self,
        destination: ConnectionDestination,
        metadata: Optional[Dict[str, str]] = None,
    ) -> CompanionInfo:
        pass

    async def disconnect(self, destination: Union[Address, str]) -> None:
        pass

    async def list_targets(self) -> List[TargetDescription]:
        pass

    async def list_xctests(self) -> List[InstalledTestInfo]:
        pass

    async def terminate(self, bundle_id: str) -> None:
        pass

    async def pull(self, bundle_id: str, src_path: str, dest_path: str) -> None:
        pass

    async def mkdir(self, bundle_id: str, path: str) -> None:
        pass

    async def list_test_bundle(self, test_bundle_id: str, app_path: str) -> List[str]:
        pass

    async def tail_logs(
        self, stop: asyncio.Event, arguments: Optional[List[str]] = None
    ) -> AsyncIterator[str]:
        yield

    async def tail_companion_logs(self, stop: asyncio.Event) -> AsyncIterator[str]:
        yield

    async def push(self, src_paths: List[str], bundle_id: str, dest_path: str) -> None:
        pass

    async def clear_keychain(self) -> None:
        pass

    async def boot(self) -> None:
        pass

    async def open_url(self, url: str) -> None:
        pass

    async def set_location(self, latitude: float, longitude: float) -> None:
        pass

    async def approve(self, bundle_id: str, permissions: Set[str]) -> None:
        pass

    async def record_video(self, stop: asyncio.Event, output_file: str) -> None:
        pass

    async def screenshot(self) -> bytes:
        pass

    async def tap(self, x: int, y: int, duration: Optional[float] = None) -> None:
        pass

    async def button(
        self, button_type: HIDButtonType, duration: Optional[float] = None
    ) -> None:
        pass

    async def key(self, keycode: int, duration: Optional[float] = None) -> None:
        return

    async def key_sequence(self, key_sequence: List[int]) -> None:
        pass

    async def swipe(
        self,
        p_start: Tuple[int, int],
        p_end: Tuple[int, int],
        delta: Optional[int] = None,
    ) -> None:
        pass

    async def crash_show(self, name: str) -> CrashLog:
        pass

    async def contacts_update(self, contacts_path: str) -> None:
        pass

    async def describe(self) -> TargetDescription:
        pass

    async def accessibility_info(
        self, point: Optional[Tuple[int, int]]
    ) -> AccessibilityInfo:
        pass

    async def run_instruments(
        self,
        stop: asyncio.Event,
        template: str,
        app_bundle_id: str,
        trace_path: str,
        post_process_arguments: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        app_args: Optional[List[str]] = None,
        started: Optional[asyncio.Event] = None,
        timings: Optional[InstrumentsTimings] = None,
    ) -> str:
        pass

    async def crash_list(self, query: CrashLogQuery) -> List[CrashLogInfo]:
        pass

    async def crash_delete(self, query: CrashLogQuery) -> List[CrashLogInfo]:
        pass

    async def add_metadata(self, metadata: Optional[Dict[str, str]]) -> None:
        pass

    async def add_media(self, file_paths: List[str]) -> None:
        pass

    async def focus(self) -> None:
        pass

    async def tail_logs_contextmanager(self) -> AsyncIterator[str]:
        yield

    async def debugserver_start(self, bundle_id: str) -> List[str]:
        pass

    async def debugserver_stop(self) -> None:
        pass

    async def debugserver_status(self) -> Optional[List[str]]:
        pass

    async def text(self, text: str) -> None:
        return

    async def ls(self, bundle_id: str, path: str) -> List[FileEntryInfo]:
        pass

    async def mv(self, bundle_id: str, src_paths: List[str], dest_path: str) -> None:
        pass

    async def rm(self, bundle_id: str, paths: List[str]) -> None:
        pass

    async def hid(self, event_iterator: AsyncIterable[HIDEvent]) -> None:
        pass

    async def kill(self) -> None:
        pass


class Server(metaclass=ABCMeta):
    def close(self) -> None:
        pass

    async def wait_closed(self) -> None:
        pass

    @property
    def ports(self) -> Dict[str, str]:
        pass
