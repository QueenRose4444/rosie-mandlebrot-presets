# Rosie_Mandlebrot community list

Places to zoom into and colour schemes, shared by people who use
[Rosie_Mandlebrot](https://github.com/QueenRose4444/rosie-mandlebrot). The app shows this list in its Library under
**Community**, where you can search it, filter it, sort it (most starred, most downloaded, newest, deepest, most
interesting) and get anything on it with one click. There is no server: the list lives here.

## How it works

- **Each entry is an issue** in this repository. Its page is where people talk about it, and a 👍 on the issue is a
  **star** (one per GitHub account).
- **Each entry is also a small file** attached to a release here (`entries`). The app downloads that file when you press
  Get, and GitHub counts every download: that is the **download count**. Nothing else is counted or tracked.
- **`index.json`** lists every entry with its stars and downloads. An Action rebuilds it every six hours and **signs** it
  (`index.json.minisig`, key `index.pub`); the app refuses an index whose signature does not check out.
- An entry is a **share code** from the app: `rmp1.…` is a place (where it is, how deep it goes, and whether it is shown
  as its Julia set), `rmc1.…` is a colour scheme (stops, inside colour and colour play). Codes are checked when they are
  listed and again by the app before anything is used.

## Sharing something

1. In the app, press **Share** on a Library card, or **Share these colours** on the Colours page, and copy the code.
2. [Open a "Share a place or colours" issue](../../issues/new?template=share.yml) and paste it in.
3. A maintainer labels it `approved`; an Action checks the code, lists it and comments on the issue. Within a few hours it
   is in everyone's Community list.

To take something off the list, a maintainer closes its issue (or labels it `removed`).

## For maintainers

- `tools/add_entry.py N` lists issue N (the `List an approved submission` workflow runs it when the `approved` label is
  added; only people with write access can add labels).
- `tools/build_index.py` and `tools/sign_index.sh` rebuild and sign the index (the `Refresh the index` workflow, every six
  hours and on demand). The signing key is the Actions secret `INDEX_SIGNING_KEY`.
- A release holds up to 1,000 files; past 900 the script opens `entries-2`, and so on. Re-uploading a file would reset its
  count, so files are never replaced.
