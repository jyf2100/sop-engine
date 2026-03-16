"""模板解析器测试。

REQ-0001-006: YAML 模板解析器
"""
import pytest
import yaml


class TestTemplateParser:
    """测试模板解析器"""

    @pytest.fixture
    def parser(self):
        """创建 TemplateParser 实例"""
        from app.services.template_parser import TemplateParser

        return TemplateParser()

    @pytest.fixture
    def valid_yaml(self):
        """合法的 YAML 模板"""
        return """
id: hello-world
name: Hello World Flow
version: "1.0.0"
description: A simple hello world flow

params:
  - name: user_name
    type: string
    required: true
    description: User's name

nodes:
  start:
    id: start
    type: start
    next: greet

  greet:
    id: greet
    type: agent
    name: Greet User
    agent_id: default
    prompt: "Hello, {user_name}!"
    output_var: greeting
    next: end

  end:
    id: end
    type: end
"""

    def test_parser_importable(self):
        """REQ-0001-006: 解析器可导入"""
        from app.services.template_parser import TemplateParser

        assert TemplateParser is not None

    def test_parse_valid_yaml(self, parser, valid_yaml):
        """REQ-0001-006: 合法 YAML 解析成功"""
        template = parser.parse(valid_yaml)

        assert template.id == "hello-world"
        assert template.name == "Hello World Flow"
        assert len(template.nodes) == 3
        assert "start" in template.nodes
        assert "greet" in template.nodes
        assert "end" in template.nodes

    def test_parse_dict(self, parser, valid_yaml):
        """REQ-0001-006: 解析字典格式"""
        data = yaml.safe_load(valid_yaml)
        template = parser.parse_dict(data)

        assert template.id == "hello-world"
        assert len(template.nodes) == 3

    def test_missing_start_node(self, parser):
        """REQ-0001-006: 缺少 start 节点抛出异常"""
        from app.services.template_parser import TemplateValidationError

        invalid_yaml = """
id: no-start
name: No Start
nodes:
  greet:
    id: greet
    type: agent
    next: end
  end:
    id: end
    type: end
"""
        with pytest.raises(TemplateValidationError, match="start"):
            parser.parse(invalid_yaml)

    def test_missing_end_node(self, parser):
        """REQ-0001-006: 缺少 end 节点抛出异常"""
        from app.services.template_parser import TemplateValidationError

        invalid_yaml = """
id: no-end
name: No End
nodes:
  start:
    id: start
    type: start
    next: greet
  greet:
    id: greet
    type: agent
"""
        with pytest.raises(TemplateValidationError, match="end"):
            parser.parse(invalid_yaml)

    def test_invalid_node_type(self, parser):
        """REQ-0001-006: 无效节点类型抛出异常"""
        from app.services.template_parser import TemplateValidationError

        invalid_yaml = """
id: bad-type
name: Bad Type
nodes:
  start:
    id: start
    type: start
    next: foo
  foo:
    id: foo
    type: invalid_type
    next: end
  end:
    id: end
    type: end
"""
        with pytest.raises(TemplateValidationError, match="type"):
            parser.parse(invalid_yaml)

    def test_invalid_next_reference(self, parser):
        """REQ-0001-006: next 引用不存在抛出异常"""
        from app.services.template_parser import TemplateValidationError

        invalid_yaml = """
id: bad-ref
name: Bad Reference
nodes:
  start:
    id: start
    type: start
    next: nonexistent
  end:
    id: end
    type: end
"""
        with pytest.raises(TemplateValidationError, match="nonexistent"):
            parser.parse(invalid_yaml)

    def test_parse_with_params(self, parser):
        """REQ-0001-006: 解析参数定义"""
        yaml_content = """
id: with-params
name: With Params
params:
  - name: count
    type: integer
    required: true
    default: 10
  - name: message
    type: string
    required: false
nodes:
  start:
    id: start
    type: start
    next: end
  end:
    id: end
    type: end
"""
        template = parser.parse(yaml_content)

        assert len(template.params) == 2
        assert template.params[0].name == "count"
        assert template.params[0].type == "integer"
        assert template.params[0].required is True
        assert template.params[0].default == 10

    def test_parse_condition_node(self, parser):
        """REQ-0001-006: 解析条件节点"""
        yaml_content = """
id: condition-flow
name: Condition Flow
nodes:
  start:
    id: start
    type: start
    next: check
  check:
    id: check
    type: condition
    branches:
      success: end
      failure: retry
  retry:
    id: retry
    type: agent
    next: end
  end:
    id: end
    type: end
"""
        template = parser.parse(yaml_content)

        assert template.nodes["check"].type == "condition"
        assert template.nodes["check"].branches == {"success": "end", "failure": "retry"}

    def test_parse_parallel_node(self, parser):
        """REQ-0001-006: 解析并行节点"""
        yaml_content = """
id: parallel-flow
name: Parallel Flow
nodes:
  start:
    id: start
    type: start
    next: parallel
  parallel:
    id: parallel
    type: parallel
    parallel_branches:
      - branch_a
      - branch_b
  branch_a:
    id: branch_a
    type: agent
    next: end
  branch_b:
    id: branch_b
    type: agent
    next: end
  end:
    id: end
    type: end
"""
        template = parser.parse(yaml_content)

        assert template.nodes["parallel"].type == "parallel"
        assert template.nodes["parallel"].parallel_branches == ["branch_a", "branch_b"]

    def test_parse_loop_node(self, parser):
        """REQ-0001-006: 解析循环节点"""
        yaml_content = """
id: loop-flow
name: Loop Flow
nodes:
  start:
    id: start
    type: start
    next: loop
  loop:
    id: loop
    type: loop
    loop_body: process
    loop_condition: "{counter} < 10"
    next: end
  process:
    id: process
    type: agent
  end:
    id: end
    type: end
"""
        template = parser.parse(yaml_content)

        assert template.nodes["loop"].type == "loop"
        assert template.nodes["loop"].loop_body == "process"
        assert template.nodes["loop"].loop_condition == "{counter} < 10"

    def test_parse_human_node(self, parser):
        """REQ-0001-006: 解析人工审批节点"""
        yaml_content = """
id: approval-flow
name: Approval Flow
nodes:
  start:
    id: start
    type: start
    next: approve
  approve:
    id: approve
    type: human
    name: Manager Approval
    approval_message: "Please approve this request"
    timeout_seconds: 3600
    next: end
  end:
    id: end
    type: end
"""
        template = parser.parse(yaml_content)

        assert template.nodes["approve"].type == "human"
        assert template.nodes["approve"].approval_message == "Please approve this request"
        assert template.nodes["approve"].timeout_seconds == 3600

    def test_parse_wait_node(self, parser):
        """REQ-0001-006: 解析等待节点"""
        yaml_content = """
id: wait-flow
name: Wait Flow
nodes:
  start:
    id: start
    type: start
    next: wait
  wait:
    id: wait
    type: wait
    wait_seconds: 60
    next: end
  end:
    id: end
    type: end
"""
        template = parser.parse(yaml_content)

        assert template.nodes["wait"].type == "wait"
        assert template.nodes["wait"].wait_seconds == 60

    def test_parse_script_node(self, parser):
        """REQ-0001-006: 解析脚本节点"""
        yaml_content = """
id: script-flow
name: Script Flow
nodes:
  start:
    id: start
    type: start
    next: run
  run:
    id: run
    type: script
    command: "echo {message}"
    output_var: output
    next: end
  end:
    id: end
    type: end
"""
        template = parser.parse(yaml_content)

        assert template.nodes["run"].type == "script"
        assert template.nodes["run"].command == "echo {message}"
        assert template.nodes["run"].output_var == "output"

    def test_validate_branch_references(self, parser):
        """REQ-0001-006: 验证条件分支引用"""
        from app.services.template_parser import TemplateValidationError

        invalid_yaml = """
id: bad-branch
name: Bad Branch
nodes:
  start:
    id: start
    type: start
    next: check
  check:
    id: check
    type: condition
    branches:
      success: nonexistent
  end:
    id: end
    type: end
"""
        with pytest.raises(TemplateValidationError, match="nonexistent"):
            parser.parse(invalid_yaml)

    def test_invalid_yaml_syntax(self, parser):
        """REQ-0001-006: 无效 YAML 语法抛出异常"""
        from app.services.template_parser import TemplateValidationError

        invalid_yaml = """
id: broken
name: [invalid
  - yaml
"""
        with pytest.raises(TemplateValidationError):
            parser.parse(invalid_yaml)
