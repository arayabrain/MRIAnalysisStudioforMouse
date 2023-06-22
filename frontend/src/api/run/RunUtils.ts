import type { FlowElement, Node } from 'react-flow-renderer'
import {
  isInputNodeData,
  isAlgorithmNodeData,
} from 'store/slice/FlowElement/FlowElementUtils'
import type {
  NodePostDataType,
  InputNodePostData,
  AlgorithmNodePostData,
} from './Run'
import { NodeData } from 'store/slice/FlowElement/FlowElementType'

export function isInputNodePostData(
  node: Node<NodePostDataType>,
): node is Node<InputNodePostData> {
  return isInputNodeData(node as FlowElement<NodeData>)
}

export function isAlgorithmNodePostData(
  node: Node<NodePostDataType>,
): node is Node<AlgorithmNodePostData> {
  return isAlgorithmNodeData(node as FlowElement<NodeData>)
}
