import { TIME_RANGES, type TimeRange } from "../../utils/chart";

type Props = {
  value: TimeRange;
  onChange: (r: TimeRange) => void;
};

export function TimeRangePicker({ value, onChange }: Props) {
  return (
    <div className="time-filters" role="tablist" aria-label="Chart range">
      {TIME_RANGES.map((r) => (
        <button
          key={r}
          type="button"
          role="tab"
          aria-selected={value === r}
          className={value === r ? "active" : undefined}
          onClick={() => onChange(r)}
        >
          {r}
        </button>
      ))}
    </div>
  );
}


