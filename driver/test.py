from wx import WX_API
if __name__ == "__main__":
    print("微信公众平台登录脚本 v1.3")
    print("="*40)
    result = WX_API.wxLogin()
    if result:
        print("\n登录结果:")
        print(f"Cookies数量: {len(result['cookies'])}")
        print(f"Token: {result['token']}")
    else:
        print("\n登录失败，请检查上述错误信息")
    print("="*40)