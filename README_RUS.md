# STAN
### Stat Analyzer for load testers

##### Библиотека STAN нацелена на упрощение анализа результатов нагрузочного тестирования за счет:
1. Унификации и стандартизации форматов данных разных источников
2. Возможности простого объединения данных разных источников по временной метке в единую структуру
3. Простой корреляции остальных данных относительно выбранной метрики
4. Простого и стандартизированного итерфейса формирования графиков (пока только с помощью plotly)

##### Библиотека STAN состоит из трёх основных модулей:
1. core		- реализует основную логику хранения и преобразования данных
2. parser	- реализует интерфейс парсеров и сами парсеры
3. plotter	- реализует интерфейс формирования графиков



## Модуль CORE
Реализует три основных класса: StanDict(dict), StanData(defaultdict), StanFlatData(defaultdict)
#### StanDict(dict)
Расширение стандартного словаря (dict). Позволяет складывать собственные инстансы и добавляет функционал фильтрации в метод keys().

Предназначен для хранения метрик за интервал времени.

#### StanData(defaultdict)
Формализует структуру данных. Наследует defaultdict. При этом принудительно во время инициализации использует StanDict, как default_factory.

Предназначен для хранения данных и манипуляций с ними. Эта структура должна быть на выходе в результате работы парсера.
##### Формат:
	StanData(timestamp1: StanDict,
             timestamp2: StanDict,
             timestamp3: StanDict,
             ...)
	
#### StanFlatData(defaultdict)
Формализует структуру данных. Наследует defaultdict. При этом принудительно во время инициализации использует list, как default_factory.

Предназначен для промежуточного хранения данных и передачи метрик на Plotter. Реализует позиционное соотношение между метриками.

Эта структура генерируется в результате вызова методов flat() или relate() класса StanData.
##### Формат:
    StanFlatData(metric1=[],
                 metric2=[],
                 metric3=[],
                 ...)

## Модуль PARSER
Формализует интерфейс парсеров и содержит непосредственно сами реализации парсеров для различных утилит.
##### На данный момент реализованы парсеры для:
1. Утилит нагрузочного тестирования:
	1. tls_meter
	2. JMeter
2. Утилит сбора показателей здоровья:
	1. Sar

## Модуль PLOTTER
Предоставляет упрощенный интерфейс для отрисовки графиков. Стандартизирует шаблоны графиков.

# User Guide
Предполагаемый цикл использования библиотеки выглядит так:

```
from stan.parser import TlsmCsvParser
from stan.parser import SarXmlParser
from stan.plotter import PlotlyGraph


TLSM_FILES = 'path_to_tlsm_csv_file_or_files'
SAR_FILE = 'path_to_sar_xml_file'
PLOT_FILE_NAME = 'path_to_graph_file'

tlsm_parser = TlsmCsvParser()
tlsm_parser.parse(TLSM_FILES)
tlsm_stat = tlsm_parser.get_stat()

sar_parser = SarXmlParser()
sar_parser.parse(SAR_FILE)
sar_stat = sar_parser.get_stat()

total_stat = tlsm_stat + sar_stat
flat_stat = total_stat.flat()

graph = PlotlyGraph('GRAPH_HEADER')
graph.append_data('METRIC_1', flat_stat['index'], flat_stat['metric_1'])
graph.append_data('METRIC_2', flat_stat['index'], flat_stat['metric_2'], y2=True)
graph.append_data('METRIC_3', flat_stat['index'], flat_stat['metric_3'], sma=True, sma_interval=10)
graph.sign_axes(x_sign='Time, s', y_sign='new title for y', y2_sign='new title for y2')
graph.plot(PLOT_FILE_NAME)
```

# Development Guide
TBC...