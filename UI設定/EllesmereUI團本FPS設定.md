# EllesmereUI 團本 FPS 畫面設定

適用：WoW Retail 12.1。

不需要安裝 EllesmereUI。以下都是 WoW 原生設定，EUI 只是一鍵代為修改。

## 建議設定：只套用團本與戰場

先開啟 WoW「選項 → 圖形 → 團隊副本與戰場設定」，再設定：

| 項目 | 設定 |
| --- | --- |
| 陰影品質 | 普通／Fair（CVar `1`） |
| 液體細節 | 關閉（`0`） |
| 粒子密度 | 高（`4`）；需要更多法術效果時才改最高（`5`） |
| SSAO／環境光遮蔽 | 關閉（`0`） |
| 景深效果 | 關閉（`0`） |
| Compute Effects | 關閉（`0`） |
| 輪廓模式 | 關閉（`0`） |
| 材質解析度 | 高（`2`） |
| 法術密度 | 必要／Essential（`0`） |
| 投射材質 | **開啟（`1`）** |
| 視野距離 | 等級 1（CVar `0`） |
| 環境細節 | 等級 1（CVar `0`） |
| 地面雜物 | 等級 1（CVar `0`） |

投射材質必須保持開啟，否則可能看不到重要地板技能。

## EUI 一鍵最佳化的原始數值

| CVar | 數值 |
| --- | ---: |
| `graphicsShadowQuality` | `1` |
| `graphicsLiquidDetail` | `0` |
| `graphicsParticleDensity` | `5` |
| `graphicsSSAO` | `0` |
| `graphicsDepthEffects` | `0` |
| `graphicsComputeEffects` | `0` |
| `graphicsOutlineMode` | `0` |
| `graphicsTextureResolution` | `2` |
| `graphicsSpellDensity` | `0` |
| `graphicsProjectedTextures` | `1` |
| `graphicsViewDistance` | `0` |
| `graphicsEnvironmentDetail` | `0` |
| `graphicsGroundClutter` | `0` |
| `RAIDsettingsEnabled` | `0` |
| `ResampleAlwaysSharpen` | `1` |
| `Sound_EnableReverb` | `0` |

EUI 還會在目前對比度不高於 55 時增加 10。這只影響畫面觀感，不影響 FPS。

`RAIDsettingsEnabled = 0` 代表 EUI 會關閉獨立團本設定，讓低負載設定套用到所有場景。一般建議維持團本設定開啟，只在團本頁套用上表。

## 還原

修改前先截圖保存原設定。不滿意時照截圖改回，或使用圖形設定頁的預設值。

## 來源

- EllesmereUI v9.0.1，commit `9ca61596c305e84cdf3244022ee387a2116b9170`
- [EUI__General_Options.lua](https://github.com/EllesmereGaming/EllesmereUI/blob/9ca61596c305e84cdf3244022ee387a2116b9170/EllesmereUIOptions/EUI__General_Options.lua#L2853-L2997)
- 查核日期：2026-08-25
