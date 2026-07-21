import { MarkerType } from "@xyflow/react";
import type {
  DependencyFlowEdge,
  ModuleFlowNode,
} from "../types/architecture";

/**
 * Temporary hardcoded graph for step 1 (static rendering).
 * Positions are hand-placed left-to-right in rough dependency order:
 * entry point -> api -> service -> repository/core.
 * ELK will take over positioning in a later step.
 */

export const sampleNodes: ModuleFlowNode[] = [
  {
    id: "app.main",
    type: "module",
    position: { x: 0, y: 180 },
    data: { module: "app.main", status: "Entry point" },
  },
  {
    id: "app.api.checkout",
    type: "module",
    position: { x: 260, y: 60 },
    data: { module: "app.api.checkout", layer: "api" },
  },
  {
    id: "app.api.orders",
    type: "module",
    position: { x: 260, y: 200 },
    data: { module: "app.api.orders", layer: "api" },
  },
  {
    id: "app.api.users",
    type: "module",
    position: { x: 260, y: 340 },
    data: { module: "app.api.users", layer: "api" },
  },
  {
    id: "app.services.payment",
    type: "module",
    position: { x: 540, y: 120 },
    data: {
      module: "app.services.payment",
      layer: "service",
      status: "Hub · 14 dependents",
    },
  },
  {
    id: "app.services.accounts",
    type: "module",
    position: { x: 540, y: 300 },
    data: { module: "app.services.accounts", layer: "service" },
  },
  {
    id: "app.repository.payment",
    type: "module",
    position: { x: 840, y: 60 },
    data: { module: "app.repository.payment", layer: "repository" },
  },
  {
    id: "app.repository.users",
    type: "module",
    position: { x: 840, y: 300 },
    data: { module: "app.repository.users", layer: "repository" },
  },
  {
    id: "app.core.config",
    type: "module",
    position: { x: 840, y: 180 },
    data: { module: "app.core.config", status: "Hub · 9 dependents" },
  },
  {
    id: "app.utils.legacy",
    type: "module",
    position: { x: 540, y: 440 },
    data: { module: "app.utils.legacy", status: "Dead module" },
  },
];

/** Arrow semantics everywhere: source imports target. */
const dependencyEdge = (
  source: string,
  target: string,
): DependencyFlowEdge => ({
  id: `${source}->${target}`,
  source,
  target,
  markerEnd: {
    type: MarkerType.ArrowClosed,
    width: 16,
    height: 16,
    color: "#6e6e6e",
  },
});

export const sampleEdges: DependencyFlowEdge[] = [
  dependencyEdge("app.main", "app.api.checkout"),
  dependencyEdge("app.main", "app.api.orders"),
  dependencyEdge("app.main", "app.api.users"),
  dependencyEdge("app.api.checkout", "app.services.payment"),
  dependencyEdge("app.api.orders", "app.services.payment"),
  dependencyEdge("app.api.users", "app.services.accounts"),
  dependencyEdge("app.services.payment", "app.repository.payment"),
  dependencyEdge("app.services.payment", "app.core.config"),
  dependencyEdge("app.services.accounts", "app.repository.users"),
  dependencyEdge("app.services.accounts", "app.core.config"),
  dependencyEdge("app.repository.payment", "app.core.config"),
];
