import { getStockMeta } from "../../data/stockMeta";
import { fmtChange, fmtPrice } from "../../utils/format";

type Props = {
  symbol: string;
  price: number | null;
  changePct: number | null;
  showBack?: boolean;
  onBack?: () => void;
};

export function StockHeader({
  symbol,
  price,
  changePct,
  showBack,
  onBack,
}: Props) {
  const meta = getStockMeta(symbol);
  const positive = (changePct ?? 0) >= 0;

  return (
    <header className="stock-header">
      <div style={{ width: "100%" }}>
        {showBack && (
          <div className="nav-row">
            <button
              type="button"
              className="icon-btn"
              aria-label="Back"
              onClick={onBack}
            >
              ←
            </button>
          </div>
        )}

        <div className="stock-identity">
          <div
            className="stock-logo"
            style={{ background: meta.logoColor }}
            aria-hidden
          >
            {meta.logoLetter}
          </div>
          <div className="stock-titles">
            <h1>{meta.name}</h1>
            <p className="sub">
              {symbol} · {meta.sector}
            </p>
          </div>
          <div className="price-block">
            <div className="price">{fmtPrice(price)}</div>
            <div className={`change ${positive ? "positive" : "negative"}`}>
              {fmtChange(changePct)}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}



