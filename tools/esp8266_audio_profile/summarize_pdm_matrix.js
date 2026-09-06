// Tables deliberately group methods by identical carrier and physical filter.
// Historical fixed-alpha controls stay in JSON, not the primary comparison.
const fs=require('node:fs'),path=require('node:path');
function summarize(result) {
  if(result.cases.length!==9 || result.common_grid_rate!==6144000) throw Error('Incomplete matrix');
  const format=value=>value==null?'Тон не обнаружен':value.toFixed(2).replace('.',',');
  const lines=[
    '# PDM / RC-PDM / Simple: одинаковые частоты выхода', '',
    `Расчёт: ${result.measured_utc}. Только численная симуляция на ПК, не запись аналогового выхода и не замер CPU ESP8266.`, '',
    '## Условия', '',
    '- Для сравнения методов используется только одна частота в пределах каждой таблицы.',
    '- Один и тот же сохранённый моно PCM: 48000 Гц, 16 бит; пять радиофрагментов и четыре синуса.',
    '- Общий физический фильтр таблиц: R=1 кОм, C=10 нФ, высокоомная нагрузка, RC=10 мкс.',
    '- Общая временная сетка — 6,144 МГц. Биты более низкой частоты удерживаются до следующего битового интервала; это не дополнительные решения модулятора.',
    '- Спектральная полоса 20 Гц–20 кГц, секундные периодические Hann-окна, без перекрытия; исключены минимум 250 мс на краях. Учтено удержание уровня GPIO. Состояние не сбрасывается между сэмплами/словами.',
    '- Нет индивидуального выравнивания громкости или задержки. В JSON также сохранены модели RC=40 мкс и пассивной нагруженной двухзвенной RC-лестницы.',
    '- Alpha обоих RC-методов выбирается по частоте: приближение `1-exp(-1/(f_bit*RC))` степенью двойки. Сдвиг увеличивается при повышении частоты.', '',
    'Здесь **15 основных сочетаний**: три метода × пять частот. Ещё восемь вариантов с постоянным alpha=1/16 служат только контролем прежних результатов, помечены `historical_fixed_alpha_control` и не участвуют в основных таблицах.', '',
    '| Частота, МГц | Новых битов/PCM | Делитель RC | Сдвиг | Внутренний RC, мкс |',
    '| ---: | ---: | ---: | ---: | ---: |'
  ];
  const groups=[];
  for(const bits of [8,16,32,64,128]) {
    const group=Object.entries(result.variants).filter(([,c])=>c.bits===bits&&c.role==='comparison');
    const names=['pdm','predictive','simple'].map(method=>{
      const entries=group.filter(([,c])=>c.method===method);
      if(entries.length!==1) throw Error('Missing/duplicated method at this frequency');
      return entries[0][0];
    });
    const rc=result.variants[names[1]],simple=result.variants[names[2]];
    if(group.length!==3 || group.some(([,c])=>c.bit_rate_hz!==bits*48000) ||
       rc.alpha!==2/bits || simple.alpha!==rc.alpha || simple.shift!==rc.shift) throw Error('Frequency/RC mismatch');
    const mhz=(bits*48000/1e6).toFixed(3).replace('.',',');
    lines.push(`| ${mhz} | ${bits} | ${1/rc.alpha} | ${rc.shift} | ${rc.internal_rc_us.toFixed(3).replace('.',',')} |`);
    groups.push({bits,names,rc,mhz});
  }
  lines.push('', 'SINAD — тон относительно шума и искажений, дБ, выше лучше. Отсутствующий тон не получает фиктивный SINAD из ошибок округления FFT.', '',
    'Радио: сигнал/ошибка относительно исходного PCM, дБ, выше лучше. Ошибка включает изменение усиления/фазы физическим RC, а не только шум. Поэтому компенсация RC может улучшать этот показатель без соответствующего изменения SINAD; обычный PDM ограничивается также действием фильтра.', '');
  for(const {names,rc,mhz} of groups) {
    lines.push(`## ${mhz} МГц; RC alpha=1/${1/rc.alpha}, shift=${rc.shift}`, '',
      '| Синус | PDM SINAD | RC-PDM SINAD | Simple SINAD |',
      '| --- | ---: | ---: | ---: |');
    for(const row of result.cases.filter(c=>c.type==='tone')) {
      lines.push(`| ${row.hz/1000} кГц, ${row.level_dbfs} dBFS | ${names.map(name=>format(row.quality.models[name].rc10us.sinad_db)).join(' | ')} |`);
    }
    lines.push('', '| Радиофрагмент | PDM сигнал/ошибка | RC-PDM сигнал/ошибка | Simple сигнал/ошибка |',
      '| --- | ---: | ---: | ---: |');
    for(const row of result.cases.filter(c=>c.type==='radio')) {
      lines.push(`| ${row.id} | ${names.map(name=>format(row.quality.models[name].rc10us.snr_to_input_db)).join(' | ')} |`);
    }
    lines.push('');
  }
  lines.push('## Проверки и ограничения', '',
    `- ${result.self_test.word_state_checks} сравнений выходного слова и конечного состояния с независимым 64-битным эталоном; ${result.self_test.grouping_checks} проверок непрерывности групп.`,
    '- Генератор проверен дополнительным BigInt-эталоном на порядок битов/байтов, крайние PCM и кадры длиннее 32 бит.',
    '- Полный путь из исходников прошивки проверен отдельно: PDM32, RC-PDM, Simple и PDM128, границы DMA и завершение/отмена вывода.',
    '- Все 72 исторических битовых потока (8 вариантов × 9 PCM) сохранили SHA-256.',
    `- Максимальное изменение старых спектральных оценок после увеличения сетки с 1,536 до 6,144 МГц: ${Math.max(...result.cases.map(c=>c.baseline_max_difference_db)).toExponential(6)} дБ; допуск теста — 0,02 дБ.`,
    '- 207 наборов результатов: 135 основных и 72 контрольных; каждый рассчитан с тремя физическими фильтрами.',
    '- Фильтр и настройки модели фиксированы до сравнения: нет индивидуального подбора под фрагмент. Точные Q16-коэффициенты в эту матрицу не входят.',
    '- Это не исследование влияния битрейта MP3/AAC, не моделирование провалов DMA, сопротивления GPIO, нагрузки USB-UART или разброса компонентов.',
    '- Прошивка и профиль по умолчанию не изменены. Более высокая выходная частота требует отдельного замера CPU/реального аналогового выхода.', '',
    '## Воспроизведение', '',
    'Нужны Node, C++17-компилятор и Python с NumPy. Пути и SHA-256 локальных PCM записаны в JSON. Радиозаписи в Git не добавлены; для точного повтора нужны сохранённые файлы. Регрессионные тесты генерируют собственные данные и не требуют записей.', '',
    '```powershell',
    'node --test tests/esp8266-pdm-matrix.test.js tests/esp8266-direct-pdm.test.js',
    'python tests/pdm_matrix_quality_model_test.py',
    'python tools/esp8266_audio_profile/measure_pdm_matrix.py --output radio_output/pdm-matrix-repeat --archive docs/benchmarks/pdm-matrix-repeat',
    'node tools/esp8266_audio_profile/summarize_pdm_matrix.js docs/benchmarks/pdm-matrix-repeat/results.json docs/benchmarks/pdm-matrix-repeat/README.md',
    '```', '',
    '[Числа, конфигурации и SHA-256](results.json), [C++/production-тесты](native-tests.log), [проверки спектральной модели](model-tests.log).', '',
    '[Общее описание, выводы, сравнение памяти и CPU](../../RC_PDM_OVERVIEW.md).', '');
  return lines.join('\n');
}
module.exports={summarize};
if(require.main===module) {
  if(!process.argv[2]) throw Error('Usage: summarize_pdm_matrix.js results.json [README.md]');
  const text=summarize(JSON.parse(fs.readFileSync(path.resolve(process.argv[2]),'utf8')));
  if(process.argv[3]) fs.writeFileSync(path.resolve(process.argv[3]),text);
  else process.stdout.write(text);
}
