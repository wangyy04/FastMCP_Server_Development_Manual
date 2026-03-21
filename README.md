# MCP服务器开发手册

本仓库为使用FastMCP开发MCP服务器的开发手册的电子资源，包括各版本开发手册的pdf文件与word原始文件、样例FastMCP项目、配置环境的安装包等。

目前的MCP服务器开发手册是基于FastMCP v2.14.5编写的。FastMCP的Github仓库为https://github.com/PrefectHQ/fastmcp

本仓库在Gitcode上的链接为https://gitcode.com/weixin_47502832/FastMCP_Server_Development_Manual

本仓库在Github上有镜像仓库，链接为https://github.com/wangyy04/FastMCP_Server_Development_Manual

## MCP_Redis_Demo目录

该目录下为作为开发手册中样例的基于Redis的中长期跨会话记忆MCP服务的Python项目文件。下载并完成环境配置后运行，即可启动这个MCP服务。可以参考其中的代码和设计思路，也可以学习如何测试一个MCP服务器等。

## examples目录

该目录下目前仅包含MCP_Test_Examples目录，该目录下为编写该开发手册时测试各种MCP组件与功能的代码。运行这些代码启动的服务器，配合MCP Inspector等调试工具，可以研究相应组件和功能的特性。代码测试的功能请参考文件名自行判断。

## release目录

该目录下为正式发行的MCP服务器开发手册pdf文件，包含各个版本的手册。

## resources目录

该目录下为离线配置Kylin服务器开发环境时部分所需的安装包，为方便读者配置环境，将这些安装包集中上传到此处，不用访问各工具的官方网站下载。

其中包括Python 3.11.9源代码安装包、OpenSSL 1.1.1f安装包、pip 23.2.1安装包、virtualenv及其依赖项安装文件合集、基于Redis的中长期跨会话记忆MCP服务项目的第三方依赖whl安装包合集。这些安装包适配于Kylin-Server-V10-SP2操作系统的服务器，Linux内核的其它操作系统能否使用不能确定。

## src目录

该目录下为各个版本的MCP服务器开发手册的word文件、开发手册封面的png文件及其原始psd文件。方便读者在本开发手册的基础上进行二次开发。但请注明原作者@wangyy04，并标注本仓库的Gitcode仓库链接或Github镜像仓库链接。