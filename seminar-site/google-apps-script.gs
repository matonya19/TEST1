/**
 * Приём заявок и анкет с сайта «Бизнес без собственника» в Google Таблицу.
 *
 * 1. Создайте Google Таблицу → Расширения → Apps Script, вставьте этот код.
 * 2. Развернуть → Новое развертывание → Тип «Веб-приложение»,
 *    «Выполнять от имени»: я, «У кого есть доступ»: все. Скопируйте URL.
 * 3. Вставьте URL в index.html → SITE_CONFIG.leadEndpoint.
 *
 * Заявки попадают на лист «Заявки», анкеты на лист «Анкеты». Общий столбец «ID» связывает их.
 */
var SHEETS = {
  registration: { name: 'Заявки', cols: ['id', 'created_at', 'name', 'contact', 'company', 'tariff', 'consent', 'utm', 'page'] },
  survey: { name: 'Анкеты', cols: ['id', 'created_at', 'sphere', 'team', 'role', 'manager', 'hours', 'returns', 'question', 'source'] }
};

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var conf = SHEETS[data.type];
    if (!conf || !data.id) return reply({ ok: false, error: 'bad_request' });
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(conf.name) || ss.insertSheet(conf.name);
    if (sheet.getLastRow() === 0) sheet.appendRow(conf.cols);
    sheet.appendRow(conf.cols.map(function (c) {
      var v = data[c];
      if (Array.isArray(v)) return v.join(', ');
      if (v && typeof v === 'object') return JSON.stringify(v);
      return v === undefined ? '' : String(v).slice(0, 2000);
    }));
    return reply({ ok: true });
  } catch (err) {
    return reply({ ok: false, error: String(err) });
  }
}

function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
