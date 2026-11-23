"""Synthetic-only MHAC-T003 recipient-repair state-machine rehearsal.

No audio output, speech recognition, physical monitoring, safety policy or human
outcome model. All times and numeric constants are fictional conventions.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

MAX_REQUESTS_PER_VERSION = 2
MAX_TOTAL_REQUESTS = 4
MIN_REPLY_BUDGET = 3
REPLY_TIMEOUT = 6
REPAIR_KINDS = frozenset({'repeat', 'which_source', 'which_event', 'what_action', 'why'})
CHANNELS = frozenset({'speech', 'button', 'text'})


class ProtocolError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _required_identifier(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProtocolError(f'invalid_{name}')
    return value


def _field(value: Any, name: str) -> str | None:
    return None if value is None else _required_identifier(value, name)


@dataclass(frozen=True)
class Message:
    message_id: str
    source_id: str | None
    event_id: str | None
    state_version: int
    issued_at: int
    expires_at: int
    latest_safe_action: int | None
    fallback_available: bool

    def __post_init__(self) -> None:
        _required_identifier(self.message_id, 'message_id')
        _field(self.source_id, 'source_id')
        _field(self.event_id, 'event_id')
        if not _integer(self.state_version) or self.state_version < 1:
            raise ProtocolError('invalid_state_version')
        if (not _integer(self.issued_at) or not _integer(self.expires_at)
                or self.expires_at <= self.issued_at):
            raise ProtocolError('invalid_validity_window')
        if self.latest_safe_action is not None and (
            not _integer(self.latest_safe_action)
            or not self.issued_at <= self.latest_safe_action <= self.expires_at
        ):
            raise ProtocolError('invalid_action_deadline')
        if not isinstance(self.fallback_available, bool):
            raise ProtocolError('invalid_fallback_available')


@dataclass
class RepairRequest:
    kind: str
    requested_at: int
    state_version: int


@dataclass
class Model:
    message: Message
    now: int = field(init=False)
    delivery: str = 'emitted'
    interpretation: str = 'unknown'
    acknowledged: bool = False
    resolution: str = 'unverified'
    action: str = 'not_reported'
    timely_action: bool | None = None
    control: str = 'none'
    pending: dict[str, RepairRequest] = field(default_factory=dict)
    seen_ids: set[str] = field(default_factory=set)
    requests_this_version: int = 0
    total_requests: int = 0
    responses: int = 0
    rejected_late_responses: int = 0
    invalidated_requests: int = 0
    deadline_missed: bool = False

    def __post_init__(self) -> None:
        self.now = self.message.issued_at

    def _same_message(self, e: dict[str, Any]) -> None:
        if (e.get('message_id') != self.message.message_id
                or e.get('state_version') != self.message.state_version):
            raise ProtocolError('message_or_version_mismatch')

    def _bound_reply(self, e: dict[str, Any]) -> None:
        self._same_message(e)
        if (e.get('source_id') != self.message.source_id
                or e.get('event_id') != self.message.event_id):
            raise ProtocolError('source_event_binding_mismatch')

    def _fallback(self, code: str) -> None:
        self.control = code if self.message.fallback_available else 'fallback_unavailable'

    def apply(self, e: dict[str, Any]) -> None:
        """Atomic transition: reject malformed events without modifying state."""
        candidate = deepcopy(self)
        candidate._apply_unchecked(e)
        self.__dict__.update(candidate.__dict__)

    def _apply_unchecked(self, e: dict[str, Any]) -> None:
        if not isinstance(e, dict) or not _integer(e.get('at')):
            raise ProtocolError('invalid_timestamp')
        t = e['at']
        if t < self.now:
            raise ProtocolError('time_reversal')
        op = e.get('op')
        if op not in {'receipt', 'interpret', 'ack', 'action', 'resolve',
                      'repair_request', 'repair_response', 'timeout', 'tick',
                      'state_update'}:
            raise ProtocolError('unsupported_operation')
        self.now = t

        if op == 'state_update':
            if e.get('message_id') != self.message.message_id:
                raise ProtocolError('message_or_version_mismatch')
            if (not _integer(e.get('state_version'))
                    or e['state_version'] != self.message.state_version + 1):
                raise ProtocolError('nonsequential_version')
            _required_identifier(e.get('provenance'), 'provenance')
            new = Message(
                message_id=self.message.message_id,
                source_id=e.get('source_id'),
                event_id=e.get('event_id'),
                state_version=e['state_version'],
                issued_at=t,
                expires_at=e.get('expires_at'),
                latest_safe_action=e.get('latest_safe_action'),
                fallback_available=e.get('fallback_available')
            )
            self.invalidated_requests += len(self.pending)
            self.message = new
            self.pending.clear()
            self.requests_this_version = 0
            self.delivery = 'emitted'
            self.interpretation = 'unknown'
            self.acknowledged = False
            self.resolution = 'unverified'
            self.action = 'not_reported'
            self.timely_action = None
            self.control = 'state_changed'
            self.deadline_missed = False
            return

        if op != 'tick':
            self._same_message(e)

        if op == 'receipt':
            self.delivery = 'reported_received'
        elif op == 'interpret':
            if e.get('status') not in {'understood', 'unclear', 'unknown'}:
                raise ProtocolError('invalid_interpretation')
            self.interpretation = e['status']
        elif op == 'ack':
            self.acknowledged = True
        elif op == 'action':
            if e.get('status') not in {'attempted', 'completed', 'unable'}:
                raise ProtocolError('invalid_action')
            self.action = e['status']
            self.timely_action = (
                e['status'] == 'completed'
                and self.message.latest_safe_action is not None
                and t <= self.message.latest_safe_action
            )
            if e['status'] == 'completed' and not self.timely_action:
                self.deadline_missed = True
        elif op == 'resolve':
            if e.get('status') not in {'resolved', 'unresolved'}:
                raise ProtocolError('invalid_resolution')
            _required_identifier(e.get('evidence_ref'), 'evidence_ref')
            self.resolution = e['status']
        elif op == 'repair_request':
            rid = _required_identifier(e.get('request_id'), 'request_id')
            if e.get('kind') not in REPAIR_KINDS:
                raise ProtocolError('unsupported_repair_kind')
            if e.get('channel') not in CHANNELS:
                raise ProtocolError('unsupported_channel')
            if rid in self.seen_ids:
                raise ProtocolError('duplicate_request_id')
            if self.control in {'deadline_fallback', 'deadline_unknown_fallback',
                                'deadline_missed_fallback', 'late_reply_discarded',
                                'response_timeout_fallback', 'message_expired_fallback',
                                'fallback_unavailable'}:
                raise ProtocolError('fallback_terminal')
            if self.pending:
                raise ProtocolError('unresolved_request')
            if (self.requests_this_version >= MAX_REQUESTS_PER_VERSION
                    or self.total_requests >= MAX_TOTAL_REQUESTS):
                raise ProtocolError('repair_budget_exceeded')
            if t >= self.message.expires_at:
                raise ProtocolError('expired_message')
            if self.message.latest_safe_action is None:
                self._fallback('deadline_unknown_fallback')
                return
            if t + MIN_REPLY_BUDGET > self.message.latest_safe_action:
                self._fallback('deadline_fallback')
                return
            self.pending[rid] = RepairRequest(e['kind'], t, self.message.state_version)
            self.seen_ids.add(rid)
            self.requests_this_version += 1
            self.total_requests += 1
            self.control = 'repair_pending'
        elif op == 'repair_response':
            self._bound_reply(e)
            rid = e.get('request_id')
            req = self.pending.get(rid)
            if req is None:
                raise ProtocolError('no_matching_pending_request')
            if req.state_version != self.message.state_version:
                raise ProtocolError('stale_request_version')
            if e.get('status') not in {'existing_info', 'cannot_answer'}:
                raise ProtocolError('unsupported_response_status')
            self.pending.pop(rid)
            if (t - req.requested_at >= REPLY_TIMEOUT
                    or t >= self.message.expires_at
                    or (self.message.latest_safe_action is not None
                        and t > self.message.latest_safe_action)):
                self.rejected_late_responses += 1
                self._fallback('late_reply_discarded')
                return
            if (e['status'] == 'existing_info'
                    and ((req.kind == 'which_source' and self.message.source_id is None)
                         or (req.kind == 'which_event' and self.message.event_id is None))):
                raise ProtocolError('unverified_unknown_promotion')
            self.responses += 1
            self.control = (
                'repair_reply_available' if e['status'] == 'existing_info'
                else 'cannot_answer'
            )
        elif op == 'timeout':
            rid = e.get('request_id')
            req = self.pending.get(rid)
            if req is None:
                raise ProtocolError('no_matching_pending_request')
            if t - req.requested_at < REPLY_TIMEOUT:
                raise ProtocolError('premature_timeout')
            self.pending.pop(rid)
            self._fallback('response_timeout_fallback')
        else:  # tick
            if (self.message.latest_safe_action is not None
                    and t > self.message.latest_safe_action
                    and self.timely_action is not True):
                self.deadline_missed = True
                self._fallback('deadline_missed_fallback')
            if t >= self.message.expires_at and self.pending:
                self.invalidated_requests += len(self.pending)
                self.pending.clear()
                self._fallback('message_expired_fallback')

    def snapshot(self) -> dict[str, Any]:
        return {
            'version': self.message.state_version,
            'delivery': self.delivery,
            'interpretation': self.interpretation,
            'acknowledged': self.acknowledged,
            'resolution': self.resolution,
            'action': self.action,
            'timely_action': self.timely_action,
            'control': self.control,
            'pending': len(self.pending),
            'requests': self.total_requests,
            'responses': self.responses,
            'late_responses': self.rejected_late_responses,
            'invalidated': self.invalidated_requests,
            'deadline_missed': self.deadline_missed,
        }


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    model = Model(Message(**case['message']))
    for event in case['events']:
        model.apply(event)
    return model.snapshot()
