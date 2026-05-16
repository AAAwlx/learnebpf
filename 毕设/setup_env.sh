#!/bin/bash
# API Key 配置助手

echo "=========================================="
echo "  Anthropic API Key 配置助手"
echo "=========================================="
echo ""

# 检查是否已设置
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✓ 检测到已设置的 API Key"
    echo ""
    echo "当前 Key: ${ANTHROPIC_API_KEY:0:10}...${ANTHROPIC_API_KEY: -4}"
    echo ""
    echo -n "是否要重新设置？[y/N]: "
    read -r reset
    if [[ ! "$reset" =~ ^[Yy]$ ]]; then
        echo "保持当前配置"
        exit 0
    fi
fi

echo ""
echo "配置 Anthropic API Key 以启用 AI 深度分析功能"
echo ""
echo "获取 API Key 的步骤："
echo "  1. 访问 https://console.anthropic.com/"
echo "  2. 注册/登录账号"
echo "  3. 在 API Keys 部分创建新密钥"
echo "  4. 复制密钥（以 sk-ant- 开头）"
echo ""
echo -n "请输入你的 API Key: "
read -r API_KEY

# 验证格式
if [[ ! "$API_KEY" =~ ^sk-ant-[a-zA-Z0-9_-]{40,}$ ]]; then
    echo ""
    echo "⚠️  警告: API Key 格式可能不正确"
    echo "正确的格式应该以 sk-ant- 开头"
    echo ""
    echo -n "仍然要保存吗？[y/N]: "
    read -r confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 1
    fi
fi

# 选择配置方式
echo ""
echo "选择配置方式："
echo "  1. 添加到 ~/.bashrc（推荐，永久生效）"
echo "  2. 添加到 ~/.zshrc（Zsh用户）"
echo "  3. 仅当前会话（临时）"
echo ""
echo -n "请选择 [1-3]: "
read -r choice

case "$choice" in
    1)
        SHELL_RC="$HOME/.bashrc"
        ;;
    2)
        SHELL_RC="$HOME/.zshrc"
        ;;
    3)
        SHELL_RC=""
        ;;
    *)
        echo "无效的选择"
        exit 1
        ;;
esac

if [ -n "$SHELL_RC" ]; then
    # 检查是否已存在
    if grep -q "ANTHROPIC_API_KEY" "$SHELL_RC" 2>/dev/null; then
        echo ""
        echo "⚠️  $SHELL_RC 中已存在 ANTHROPIC_API_KEY 配置"
        echo -n "是否要覆盖？[y/N]: "
        read -r overwrite
        if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
            echo "已取消"
            exit 0
        fi
        # 删除旧行
        sed -i '/export ANTHROPIC_API_KEY/d' "$SHELL_RC"
    fi

    # 添加新配置
    echo "" >> "$SHELL_RC"
    echo "# Anthropic API Key for netfilter_trace AI analysis" >> "$SHELL_RC"
    echo "export ANTHROPIC_API_KEY=\"$API_KEY\"" >> "$SHELL_RC"

    echo ""
    echo "✓ API Key 已添加到 $SHELL_RC"
    echo ""
    echo "请运行以下命令使配置生效："
    echo "  source $SHELL_RC"
    echo ""
    echo "或重新打开终端"
else
    export ANTHROPIC_API_KEY="$API_KEY"
    echo ""
    echo "✓ API Key 已设置为当前会话"
    echo "注意：关闭终端后将失效"
fi

echo ""
echo "测试 API Key..."
echo ""

# 测试调用
if command -v python3 &> /dev/null; then
    python3 -c "
import sys
try:
    from anthropic import Anthropic
    client = Anthropic(api_key='$API_KEY')
    print('✓ API Key 验证成功')
    print('✓ 可以使用 AI 深度分析功能')
except ImportError:
    print('⚠️  未安装 anthropic 库')
    print('   安装命令: pip3 install anthropic')
    print('   或使用本地分析模式（无需 API）')
except Exception as e:
    print(f'✗ API Key 验证失败: {e}')
    sys.exit(1)
" 2>/dev/null
else
    echo "⚠️  未找到 python3，无法验证 API Key"
fi

echo ""
echo "配置完成！"
echo ""
echo "使用方法："
echo "  ./netfilter_wrapper.sh"
echo "  → 选择 8 (AI分析)"
echo "  → 选择 2 (AI深度分析)"
echo ""
