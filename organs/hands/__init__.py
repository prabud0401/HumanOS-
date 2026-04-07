"""
Hands Organ — Agent control and task execution for HumanOS.

Executes actions decided by the Brain: shell commands, GitHub and Azure DevOps
automation, and delegated agent work. Logs every execution for audit and rollback.
"""

default_app_config = "organs.hands.apps.HandsConfig"
