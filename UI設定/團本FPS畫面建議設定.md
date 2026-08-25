# 團本 FPS 畫面建議設定

適用：WoW Retail 12.1。

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
| 視野距離 | 等級 4（CVar `3`） |
| 環境細節 | 等級 1（CVar `0`） |
| 地面雜物 | 等級 1（CVar `0`） |

投射材質必須保持開啟，否則可能看不到重要地板技能。

## CVar 對照

| CVar | 數值 |
| --- | ---: |
| `RAIDsettingsEnabled` | `1` |
| `raidGraphicsShadowQuality` | `1` |
| `raidGraphicsLiquidDetail` | `0` |
| `raidGraphicsParticleDensity` | `4` |
| `raidGraphicsSSAO` | `0` |
| `raidGraphicsDepthEffects` | `0` |
| `raidGraphicsComputeEffects` | `0` |
| `raidGraphicsOutlineMode` | `0` |
| `raidGraphicsTextureResolution` | `2` |
| `raidGraphicsSpellDensity` | `0` |
| `raidGraphicsProjectedTextures` | `1` |
| `raidGraphicsViewDistance` | `3` |
| `raidGraphicsEnvironmentDetail` | `0` |
| `raidGraphicsGroundClutter` | `0` |
| `ResampleAlwaysSharpen` | `1` |
| `Sound_EnableReverb`（選用） | `0` |

粒子密度需要更多法術效果時，可將 `raidGraphicsParticleDensity` 改為 `5`。對比度維持個人偏好即可，與 FPS 無關。

## 可直接貼入遊戲的指令

在遊戲聊天框中逐行貼上：

```text
/console RAIDsettingsEnabled 1
/console raidGraphicsShadowQuality 1
/console raidGraphicsLiquidDetail 0
/console raidGraphicsParticleDensity 4
/console raidGraphicsSSAO 0
/console raidGraphicsDepthEffects 0
/console raidGraphicsComputeEffects 0
/console raidGraphicsOutlineMode 0
/console raidGraphicsTextureResolution 2
/console raidGraphicsSpellDensity 0
/console raidGraphicsProjectedTextures 1
/console raidGraphicsViewDistance 3
/console raidGraphicsEnvironmentDetail 0
/console raidGraphicsGroundClutter 0
/console ResampleAlwaysSharpen 1
```

選用：關閉音效殘響。

```text
/console Sound_EnableReverb 0
```

需要更多法術粒子效果時使用：

```text
/console raidGraphicsParticleDensity 5
```

極限效能選項：視野距離降至最低。近距離戰鬥內容仍會顯示，但遠方地形或物件可能較晚出現。

```text
/console raidGraphicsViewDistance 0
```

## 還原

修改前先截圖保存原設定。不滿意時照截圖改回，或使用圖形設定頁的預設值。
