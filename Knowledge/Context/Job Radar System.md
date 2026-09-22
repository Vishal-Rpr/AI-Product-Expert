# Job Radar System

**Created:** 14 Aug 2026  
**Live sheet:** https://docs.google.com/spreadsheets/d/1g5tZ2S6GmeYYgxjIXNzYoEyw84sMIbxM7GA6_NkXcjs/edit  
**Tab:** Jobs  
**Code:** `C:\Users\user\Desktop\job-radar` (scanner) and `job_radar/` in this workspace  
**Linked goal:** Land an AI PM role (`GOALS.md`)

## Rule
Append new job URLs only. Never rewrite existing rows (status, applied date, comments).

## Targeting
India, Dubai/UAE, fully remote. SPM / platform PM / AI-native PM. No LinkedIn scrape. No auto-apply.

## Write path
Cursor Drive/Sheets MCP is often on a different Google account than the sheet owner (`vishalraviprabhakar@gmail.com`), so MCP writes 403. Use the Sheets API with an owner OAuth token, or paste from CSV while logged in as owner.
