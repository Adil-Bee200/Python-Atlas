type Props = {
  onClose?: () => void;
};

export function TradeActions({ onClose }: Props) {
  if (!onClose) return null;

  return (
    <div className="trade-fabs">
      <button type="button" className="trade-btn close" onClick={onClose}>
        Close
      </button>
    </div>
  );
}
