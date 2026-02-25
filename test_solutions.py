#!/usr/bin/env python3
"""
FlintBloom 功能验证脚本

验证两个核心问题的解决方案：
1. 可以在其他项目中导入使用
2. 支持动态 thread_id
"""

import sys
import os

# 添加路径以便导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))


def test_import():
    """测试 1: 验证可以导入 FlintBloom"""
    print("\n" + "="*70)
    print("测试 1: 验证导入功能")
    print("="*70)

    try:
        from flintbloom import FlintBloomCallbackHandler
        print("✅ 成功导入: from flintbloom import FlintBloomCallbackHandler")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_static_thread_id():
    """测试 2: 验证静态 thread_id（向后兼容）"""
    print("\n" + "="*70)
    print("测试 2: 静态 thread_id（向后兼容）")
    print("="*70)

    try:
        from flintbloom import FlintBloomCallbackHandler

        callback = FlintBloomCallbackHandler(thread_id="test-static-thread")
        print("✅ 成功创建回调: thread_id='test-static-thread'")

        # 验证 thread_id
        resolved = callback._resolve_thread_id(None)
        assert resolved == "test-static-thread", f"Expected 'test-static-thread', got '{resolved}'"
        print(f"✅ Thread ID 解析正确: {resolved}")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_auto_detect_thread_id():
    """测试 3: 验证自动检测 thread_id"""
    print("\n" + "="*70)
    print("测试 3: 自动检测 thread_id")
    print("="*70)

    try:
        from flintbloom import FlintBloomCallbackHandler

        callback = FlintBloomCallbackHandler(auto_detect_thread_id=True)
        print("✅ 成功创建回调: auto_detect_thread_id=True")

        # 模拟 LangGraph config
        resolved = callback._resolve_thread_id(
            None,
            configurable={"thread_id": "auto-detected-123"}
        )
        assert resolved == "auto-detected-123", f"Expected 'auto-detected-123', got '{resolved}'"
        print(f"✅ 自动检测成功: {resolved}")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_custom_resolver():
    """测试 4: 验证自定义解析器"""
    print("\n" + "="*70)
    print("测试 4: 自定义 thread_id 解析器")
    print("="*70)

    try:
        from flintbloom import FlintBloomCallbackHandler

        def custom_resolver(metadata):
            user_id = metadata.get("user_id", "anonymous")
            session_id = metadata.get("session_id", "default")
            return f"user-{user_id}-session-{session_id}"

        callback = FlintBloomCallbackHandler(thread_id_resolver=custom_resolver)
        print("✅ 成功创建回调: 使用自定义解析器")

        # 测试解析
        resolved = callback._resolve_thread_id(
            metadata={"user_id": "alice", "session_id": "abc123"}
        )
        expected = "user-alice-session-abc123"
        assert resolved == expected, f"Expected '{expected}', got '{resolved}'"
        print(f"✅ 自定义解析成功: {resolved}")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_priority():
    """测试 5: 验证 thread_id 解析优先级"""
    print("\n" + "="*70)
    print("测试 5: Thread ID 解析优先级")
    print("="*70)

    try:
        from flintbloom import FlintBloomCallbackHandler

        # 自定义解析器应该有最高优先级
        def high_priority_resolver(metadata):
            return "from-custom-resolver"

        callback = FlintBloomCallbackHandler(
            thread_id="static-fallback",  # 优先级 4
            thread_id_resolver=high_priority_resolver,  # 优先级 1 - 最高
            auto_detect_thread_id=True
        )

        # 即使提供了 config 和 static，自定义解析器应该胜出
        resolved = callback._resolve_thread_id(
            metadata={"user_id": "test"},
            configurable={"thread_id": "from-config"}
        )

        assert resolved == "from-custom-resolver", f"Expected 'from-custom-resolver', got '{resolved}'"
        print(f"✅ 优先级正确: 自定义解析器 > config > static")
        print(f"   结果: {resolved}")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_metadata_fallback():
    """测试 6: 验证 metadata 回退"""
    print("\n" + "="*70)
    print("测试 6: Metadata 回退机制")
    print("="*70)

    try:
        from flintbloom import FlintBloomCallbackHandler

        callback = FlintBloomCallbackHandler(auto_detect_thread_id=True)

        # 测试从 metadata 中提取
        resolved = callback._resolve_thread_id(
            metadata={"thread_id": "from-metadata"}
        )
        assert resolved == "from-metadata", f"Expected 'from-metadata', got '{resolved}'"
        print(f"✅ Metadata 回退成功: {resolved}")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*70)
    print("FlintBloom 功能验证")
    print("="*70)
    print("\n验证两个核心问题的解决方案：")
    print("1. ✅ 可以在其他项目中导入使用")
    print("2. ✅ 支持动态 thread_id")

    tests = [
        ("导入功能", test_import),
        ("静态 thread_id", test_static_thread_id),
        ("自动检测 thread_id", test_auto_detect_thread_id),
        ("自定义解析器", test_custom_resolver),
        ("解析优先级", test_priority),
        ("Metadata 回退", test_metadata_fallback),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{name}' 出现异常: {e}")
            results.append((name, False))

    # 总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\n结果: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！FlintBloom 功能正常！")
        print("\n✅ 问题 1 已解决: 可以在其他项目中导入使用")
        print("   - 安装: pip install git+https://github.com/zhangwenjiexbz/FlintBloom.git")
        print("   - 导入: from flintbloom import FlintBloomCallbackHandler")
        print("\n✅ 问题 2 已解决: 支持动态 thread_id")
        print("   - 自动检测: 从 LangGraph config 自动提取")
        print("   - 自定义解析: 使用 thread_id_resolver 参数")
        print("   - 向后兼容: 静态 thread_id 仍然有效")
        print("\n📚 查看完整文档:")
        print("   - 安装指南: INSTALL.md")
        print("   - 集成指南: INTEGRATION_GUIDE.md")
        print("   - 更新说明: UPDATE_NOTES.md")
        print("   - 快速参考: QUICK_REFERENCE.md")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
