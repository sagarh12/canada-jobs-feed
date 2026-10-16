/**
 * Starts the canada-jobs-feed workflow every 10 minutes.
 *
 * GitHub's own schedule runs far less often than asked when GitHub is busy (every 1–2 hours
 * instead of every 10–30 minutes), so this Google Apps Script project starts the workflow
 * itself. The workflow decides whether to do a full run or a quick employer-only run.
 *
 * Set up (once):
 *   1. script.google.com → New project → paste this file → save.
 *   2. Project Settings (gear) → Script properties → Add property:
 *        GITHUB_TOKEN = a fine-grained GitHub token for sagarh12/canada-jobs-feed with
 *        "Actions: Read and write" permission (nothing else).
 *   3. Select setUp in the toolbar → Run → approve the permissions.
 * To stop: run stop, or delete the project.
 */
const REPO = 'sagarh12/canada-jobs-feed';
const WORKFLOW = 'feed.yml';
const EVERY_MINUTES = 10;

function triggerFeed() {
  const token = PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  if (!token) throw new Error('Add the GITHUB_TOKEN script property first (Project Settings → Script properties).');
  const res = UrlFetchApp.fetch(`https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches`, {
    method: 'post',
    contentType: 'application/json',
    muteHttpExceptions: true,
    headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' },
    payload: JSON.stringify({ ref: 'main', inputs: { mode: 'auto' } }),
  });
  // 204 = started. 401 = token wrong or expired. 403/404 = token can't reach this repo's Actions.
  if (res.getResponseCode() !== 204) throw new Error(`GitHub said ${res.getResponseCode()}: ${res.getContentText().slice(0, 200)}`);
}

// Run once: starts the feed now, then every EVERY_MINUTES minutes.
function setUp() {
  stop();
  triggerFeed();
  ScriptApp.newTrigger('triggerFeed').timeBased().everyMinutes(EVERY_MINUTES).create();
}

function stop() {
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
}
