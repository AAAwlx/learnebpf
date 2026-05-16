#!/usr/bin/env python3
"""
netfilter_trace AI 分析器
实时分析网络监控数据，生成智能报告
"""

import sys
import re
import json
import time
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import argparse

# 尝试导入 anthropic（如果安装）
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("警告: 未安装 anthropic 库，将使用本地分析模式")
    print("安装命令: pip install anthropic")


class NetflowRecord:
    """网络流记录"""
    def __init__(self, raw_line: str):
        self.raw = raw_line.strip()
        self.timestamp = datetime.now()
        self.func = None
        self.src_ip = None
        self.dst_ip = None
        self.skb = None
        self.hook_num = None
        self.result = None
        self.parse()

    def parse(self):
        """解析日志行"""
        # 解析函数名格式: [func_name]
        func_match = re.search(r'\[([^\]]+)\]', self.raw)
        if func_match:
            self.func = func_match.group(1)

        # 解析IP地址
        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s*->\s*(\d+\.\d+\.\d+\.\d+)', self.raw)
        if ip_match:
            self.src_ip = ip_match.group(1)
            self.dst_ip = ip_match.group(2)

        # 解析skb地址
        skb_match = re.search(r'skb:\s*0x([0-9a-f]+)|skb=\s*0x([0-9a-f]+)', self.raw)
        if skb_match:
            self.skb = skb_match.group(1) or skb_match.group(2)

        # 解析hook编号
        hook_match = re.search(r'hook_num:(\d+)', self.raw)
        if hook_match:
            self.hook_num = int(hook_match.group(1))

        # 解析结果（ACCEPT/DROP）
        if '[ACCEPT]' in self.raw:
            self.result = 'ACCEPT'
        elif '[DROP]' in self.raw:
            self.result = 'DROP'
        elif '[OTHER=' in self.raw:
            self.result = 'OTHER'

    def is_valid(self) -> bool:
        """检查记录是否有效"""
        return self.func is not None and self.src_ip is not None


class NetworkAnalyzer:
    """网络流量分析器"""

    # Hook编号映射
    HOOK_NAMES = {
        0: "NF_INET_PRE_ROUTING",
        1: "NF_INET_LOCAL_IN",
        2: "NF_INET_FORWARD",
        3: "NF_INET_LOCAL_OUT",
        4: "NF_INET_POST_ROUTING"
    }

    def __init__(self):
        self.records: List[NetflowRecord] = []
        self.stats = {
            'total_packets': 0,
            'accept_packets': 0,
            'drop_packets': 0,
            'unique_sources': set(),
            'unique_destinations': set(),
            'hook_distribution': Counter(),
            'function_calls': Counter(),
            'ip_pairs': Counter(),
            'skb_tracking': defaultdict(list)
        }

    def add_record(self, record: NetflowRecord):
        """添加记录"""
        if not record.is_valid():
            return

        self.records.append(record)
        self.stats['total_packets'] += 1

        if record.result:
            if record.result == 'ACCEPT':
                self.stats['accept_packets'] += 1
            elif record.result == 'DROP':
                self.stats['drop_packets'] += 1

        if record.src_ip:
            self.stats['unique_sources'].add(record.src_ip)
        if record.dst_ip:
            self.stats['unique_destinations'].add(record.dst_ip)

        if record.hook_num is not None:
            self.stats['hook_distribution'][record.hook_num] += 1

        if record.func:
            self.stats['function_calls'][record.func] += 1

        if record.src_ip and record.dst_ip:
            pair = f"{record.src_ip} -> {record.dst_ip}"
            self.stats['ip_pairs'][pair] += 1

        if record.skb:
            self.stats['skb_tracking'][record.skb].append(record)

    def analyze_local(self) -> str:
        """本地分析（不使用AI）"""
        if not self.records:
            return "暂无数据可分析"

        report = []
        report.append("=" * 60)
        report.append("📊 网络流量分析报告")
        report.append("=" * 60)
        report.append(f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"📦 记录总数: {self.stats['total_packets']} 条")
        report.append("")

        # 1. 概览统计
        report.append("📈 总体统计")
        report.append("-" * 60)
        total = self.stats['total_packets']
        accept = self.stats['accept_packets']
        drop = self.stats['drop_packets']

        if accept + drop > 0:
            accept_rate = (accept / (accept + drop)) * 100
            drop_rate = (drop / (accept + drop)) * 100
            report.append(f"  接受 (ACCEPT): {accept} ({accept_rate:.1f}%)")
            report.append(f"  丢弃 (DROP):   {drop} ({drop_rate:.1f}%)")
        else:
            report.append("  无结果判定数据")

        report.append(f"  唯一源IP: {len(self.stats['unique_sources'])} 个")
        report.append(f"  唯一目标IP: {len(self.stats['unique_destinations'])} 个")
        report.append("")

        # 2. 热门Hook点
        if self.stats['hook_distribution']:
            report.append("🎣 Hook 点分布")
            report.append("-" * 60)
            for hook_num, count in self.stats['hook_distribution'].most_common():
                hook_name = self.HOOK_NAMES.get(hook_num, f"Unknown({hook_num})")
                pct = (count / total) * 100
                report.append(f"  {hook_name}: {count} 次 ({pct:.1f}%)")
            report.append("")

        # 3. 函数调用频率
        if self.stats['function_calls']:
            report.append("⚙️  函数调用TOP5")
            report.append("-" * 60)
            for func, count in self.stats['function_calls'].most_common(5):
                pct = (count / total) * 100
                report.append(f"  {func}: {count} 次 ({pct:.1f}%)")
            report.append("")

        # 4. 热门IP流
        if self.stats['ip_pairs']:
            report.append("🌐 热门IP流 TOP5")
            report.append("-" * 60)
            for pair, count in self.stats['ip_pairs'].most_common(5):
                pct = (count / total) * 100
                report.append(f"  {pair}: {count} 次 ({pct:.1f}%)")
            report.append("")

        # 5. 安全分析
        report.append("🔒 安全分析")
        report.append("-" * 60)

        if drop > 0:
            drop_rate = (drop / (accept + drop)) * 100
            if drop_rate > 10:
                report.append(f"  ⚠️  警告: 丢包率较高 ({drop_rate:.1f}%)")
            else:
                report.append(f"  ✓ 丢包率正常 ({drop_rate:.1f}%)")
        else:
            report.append("  ✓ 无丢包")

        # 检查异常IP
        private_ips = [ip for ip in self.stats['unique_sources']
                      if ip.startswith(('192.168.', '10.', '172.16.'))]
        public_ips = self.stats['unique_sources'] - set(private_ips)

        if public_ips:
            report.append(f"  ℹ️  检测到 {len(public_ips)} 个公网IP访问")
        if private_ips:
            report.append(f"  ℹ️  检测到 {len(private_ips)} 个内网IP访问")

        report.append("")

        # 6. 性能分析
        if self.stats['skb_tracking']:
            report.append("⚡ SKB 生命周期分析")
            report.append("-" * 60)
            skb_counts = {skb: len(recs) for skb, recs in self.stats['skb_tracking'].items()}
            if skb_counts:
                avg_hops = sum(skb_counts.values()) / len(skb_counts)
                report.append(f"  平均处理步数: {avg_hops:.1f} 次")
                max_skb = max(skb_counts, key=skb_counts.get)
                report.append(f"  最多步数: {skb_counts[max_skb]} 次")
            report.append("")

        # 7. 建议
        report.append("💡 优化建议")
        report.append("-" * 60)

        if drop > accept:
            report.append("  ⚠️  丢包率过高，建议检查:")
            report.append("     - 防火墙规则是否过于严格")
            report.append("     - 是否有DDoS攻击")
            report.append("     - 网络连接是否正常")

        if len(self.stats['unique_sources']) > 100:
            report.append("  ℹ️  连接数较多，建议:")
            report.append("     - 检查是否有异常连接")
            report.append("     - 考虑增加连接跟踪限制")

        if not self.stats['function_calls']['nf_hook_slow']:
            report.append("  ℹ️  未检测到netfilter钩子，可能:")
            report.append("     - 规则链配置不完整")
            report.append("     - 使用了非标准netfilter配置")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

    def analyze_with_ai(self, api_key: str = None) -> str:
        """使用Claude AI进行深度分析"""
        if not ANTHROPIC_AVAILABLE:
            return self.analyze_local()

        if not api_key:
            return "错误: 需要提供 Anthropic API Key"

        try:
            client = anthropic.Anthropic(api_key=api_key)

            # 准备上下文数据
            context = self._prepare_ai_context()

            prompt = f"""你是一个网络安全专家。请分析以下网络监控数据，生成一份详细报告。

监控数据统计:
{json.dumps(context, indent=2, ensure_ascii=False)}

请提供:
1. 流量模式分析
2. 安全风险评估
3. 性能瓶颈识别
4. 具体优化建议

请用中文回答，格式清晰。"""

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            ai_report = message.content[0].text

            # 组合报告
            local_report = self.analyze_local()
            combined = f"{local_report}\n\n" + "=" * 60 + "\n"
            combined += "🤖 AI 深度分析\n" + "=" * 60 + "\n\n"
            combined += ai_report

            return combined

        except Exception as e:
            return f"AI分析失败: {str(e)}\n\n{self.analyze_local()}"

    def _prepare_ai_context(self) -> Dict:
        """准备AI分析所需的上下文"""
        return {
            '统计信息': {
                '总包数': self.stats['total_packets'],
                '接受': self.stats['accept_packets'],
                '丢弃': self.stats['drop_packets'],
                '唯一源IP数': len(self.stats['unique_sources']),
                '唯一目标IP数': len(self.stats['unique_destinations']),
            },
            'Hook分布': dict(self.stats['hook_distribution']),
            '热门函数': dict(self.stats['function_calls'].most_common(10)),
            '热门IP流': dict(self.stats['ip_pairs'].most_common(10)),
            '最近记录': [r.raw for r in self.records[-20:]]
        }


def read_stream(file_handle):
    """从流中读取行"""
    for line in file_handle:
        yield line


def main():
    parser = argparse.ArgumentParser(description='网络流量AI分析器')
    parser.add_argument('--mode', choices=['stream', 'file'], default='stream',
                       help='运行模式: stream(实时) 或 file(文件)')
    parser.add_argument('--file', help='日志文件路径')
    parser.add_argument('--api-key', help='Anthropic API Key (可选)')
    parser.add_argument('--interval', type=int, default=30,
                       help='实时模式下报告间隔(秒)')
    parser.add_argument('--min-records', type=int, default=10,
                       help='最小记录数才生成报告')

    args = parser.parse_args()

    analyzer = NetworkAnalyzer()
    start_time = time.time()
    last_report_time = time.time()

    print("🚀 网络流量分析器已启动")
    print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 最小记录数: {args.min_records}")
    print(f"⏱️  报告间隔: {args.interval} 秒")
    print("-" * 60)

    try:
        if args.mode == 'file':
            # 文件模式
            if not args.file:
                print("错误: 文件模式需要指定 --file 参数")
                sys.exit(1)

            print(f"📂 读取文件: {args.file}")
            with open(args.file, 'r') as f:
                for line in f:
                    record = NetflowRecord(line)
                    analyzer.add_record(record)

            # 生成最终报告
            if args.api_key and ANTHROPIC_AVAILABLE:
                print("\n🤖 使用AI分析中...")
                report = analyzer.analyze_with_ai(args.api_key)
            else:
                report = analyzer.analyze_local()

            print("\n" + report)

        else:
            # 流模式 - 实时分析
            print("💡 提示: 从标准输入读取数据，按 Ctrl+C 埥看报告并退出")
            print("-" * 60)

            for line in sys.stdin:
                record = NetflowRecord(line)
                analyzer.add_record(record)

                # 定期生成报告
                if (time.time() - last_report_time >= args.interval and
                    len(analyzer.records) >= args.min_records):

                    print(f"\n{'=' * 60}")
                    print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - 实时报告")
                    print(f"{'=' * 60}")

                    if args.api_key and ANTHROPIC_AVAILABLE:
                        report = analyzer.analyze_with_ai(args.api_key)
                    else:
                        report = analyzer.analyze_local()

                    print(report)
                    last_report_time = time.time()

    except KeyboardInterrupt:
        duration = time.time() - start_time

        print(f"\n\n{'=' * 60}")
        print("⏹️  监控已停止")
        print(f"{'=' * 60}")
        print(f"⏱️  运行时长: {duration:.1f} 秒")
        print(f"📦 总记录数: {len(analyzer.records)}")
        print(f"")

        # 生成最终报告
        if len(analyzer.records) >= args.min_records:
            if args.api_key and ANTHROPIC_AVAILABLE:
                print("🤖 使用AI生成最终报告...")
                report = analyzer.analyze_with_ai(args.api_key)
            else:
                report = analyzer.analyze_local()

            print("\n" + report)
        else:
            print(f"⚠️  记录数不足 ({len(analyzer.records)} < {args.min_records})，无法生成报告")


if __name__ == '__main__':
    main()
