# Locator Update

## Goal

A locator change must not force an identity change or a new application-level peer binding. Internet-X therefore treats mobility as an authenticated locator-management operation within an existing flow.

## Packet Types

- `LOCATOR_UPDATE`
- `LOCATOR_UPDATE_ACK`

## LOCATOR_UPDATE Fields

Top-level:

- `session_id`
- `flow_id`
- `sequence` set to the update counter
- `locator_hint` set to the new claimed locator

Payload:

- `new_locator`
- `previous_locator`
- `update_counter`
- `signature`
- `update_mac`

## Validation Rules

The receiver must:

1. verify that the packet's `flow_id` matches an established flow,
2. verify that `update_counter` is greater than the last accepted update counter,
3. verify the sender signature over the update fields,
4. verify the MAC using the session's update key,
5. only then replace the stored active locator.

## ACK Behavior

`LOCATOR_UPDATE_ACK` returns:

- `acknowledged_counter`
- `active_locator`
- server signature
- server MAC

## Security Motivation

Unauthenticated rebinding is a locator hijack path. The repository therefore treats locator update as security-critical control traffic.
