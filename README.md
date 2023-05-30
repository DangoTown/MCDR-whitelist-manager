# Whitelist Manager

一个基于 [MCDR-offline-whitelist-manager](https://github.com/Lazy-Bing-Server/MCDR-offline-whitelist-manager) 的插件，补全了对正版用户白名单的支持

## 起因
因服务器运营需要，由正版验证切换到基于 [MultiYggdrasil](https://github.com/YuxuanZuo/MultiYggdrasil) 实现的外置+正版共存验证时发现使用 `/whitelist add <player>` 添加的白名单变成了使用 version3 算法生成的盗版uuid，但是服务器是同时存在正版玩家的，所以需要一个能添加正版玩家白名单的插件。然后就想起了 [SinBing](https://github.com/Sinbing) 写的离线白名单插件，拿来稍微修改一下就能用了。


## 快速开始

### 	安装

​		本插件为单文件，将本体 `WhitelistManager.py` 放入插件目录 `/plugin/` 可完成安装，

​		随后需要使用MCDR命令`!!MCDR r plg`以载入插件。



### 	配置

​		本插件使用懒狗狂喜的 **硬编码** 存储配置信息，修改区域位于插件前面几行（如图）

​		如 **服务端文件夹** 或 **存档文件夹** 修改过名称，需要修改配置信息。

​		`server_dirname: 服务端文件夹名称`		`world_dirname: 存档文件夹名称`

![hard_config](https://github.com/Lazy-Bing-Server/MCDR-offline-whitelist-manager/blob/main/pic/hard_config.png)


​		余下配置信息 **请不要** 修改，此处仅做介绍。

​		`offline_uuid_method: 获取离线UUID方法(int, 默认：3，推荐：3)`

​		**修改离线UUID获取方法不影响正版UUID的获取**，正版只支持通过方法1获取

​		方法1：通过API获取UUID。

​		方法2：通过carpet bot + 比较 playerdata的方式获取离线UUID，需要服务器安装有Carpet Mod。

​		**## 方法2对于同一昵称仅能添加一次白名单（意味着删白名等同于永久BAN）。不推荐 ##**

​		方法3：通过按照mojang规则本地计算离线UUID。

​		`bot_wait_time: 方法2时等待Carpet bot的时间(int, 默认: 3)`



### 	命令

​		`!!wlist help`

​			显示插件帮助信息。



​		`!!wlist add [player name] (online)`

​			添加玩家至服务器白名单，添加正版玩家时需要加上online参数(可缩写为o)，**# 该命令需要MCDR权限ADMIN及以上 #**。

​			![wlist_add](https://github.com/Lazy-Bing-Server/MCDR-offline-whitelist-manager/blob/main/pic/wlist_add.png)



​		`!!wlist remove [player name]`

​			从服务器白名单中移出玩家，**# 该命令需要MCDR权限ADMIN及以上 #**。

​			![wlist_remove](https://github.com/Lazy-Bing-Server/MCDR-offline-whitelist-manager/blob/main/pic/wlist_remove.png)



​		`!!wlist list`

​			显示服务器白名单列表，**# 该命令需要MCDR权限ADMIN及以上 #**。

​			![wlist_list](https://github.com/Lazy-Bing-Server/MCDR-offline-whitelist-manager/blob/main/pic/wlist_list.png)



### 	备份

​		每次操作白名单(Add/Remove)时都会生成一次备份，备份位于 `/server/whitelist_backup/`

​		备份中会使用 **A / R** 记录本次备份时的操作类型 添加 / 删除 。（意味这备份是X操作前保存的）

​		![backup_whitelist](https://github.com/Lazy-Bing-Server/MCDR-offline-whitelist-manager/blob/main/pic/backup_whitelist.png)


## 鸣谢

​	[原仓库鸣谢列表](​https://github.com/DangoTown/MCDR-whitelist-manager#鸣谢) 以及 [SinBing](https://github.com/Sinbing)
