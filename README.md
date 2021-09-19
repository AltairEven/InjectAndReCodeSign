# InjectAndReCodeSign
为iOS ipa替换动态库，并且重签名

# 运行环境
Python版本： 2.7

系统环境：MacOS

# 使用说明
1、将`InjectAndReCodeSign.py`放在`IpaName.ipa`同级目录

2、将待注入的动态库文件，放在`injectionFolderName`目录

3、执行脚本
```shell
python InjectAndReCodeSign.py IpaName.ipa "Apple Development: account (******)" embedded.mobileprovision com.altair.bundleId 'NewIpaName' injectionFolderName
```

# 参考文章
[《iOS动态库注入》](https://altaireven.github.io/Altair/iOS/iOS动态库注入)