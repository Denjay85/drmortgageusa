"use client";

import {
  useEffect,
  useRef,
  useState,
  type InputHTMLAttributes,
} from "react";

type CalculatorNumberInputProps = Omit<
  InputHTMLAttributes<HTMLInputElement>,
  "onChange" | "type" | "value"
> & {
  value: number;
  onValueChange: (value: number) => void;
};

/**
 * A numeric calculator field that lets a user fully clear a default zero.
 * While empty, the calculator receives 0, but the field stays visually blank
 * until the user types a replacement value or an external scenario updates it.
 */
export default function CalculatorNumberInput({
  value,
  onValueChange,
  onBlur,
  ...props
}: CalculatorNumberInputProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const normalizedValue = Number.isFinite(value) ? value : 0;
  const [rawValue, setRawValue] = useState(String(normalizedValue));

  useEffect(() => {
    if (document.activeElement !== inputRef.current) {
      setRawValue(String(normalizedValue));
    }
  }, [normalizedValue]);

  return (
    <input
      {...props}
      ref={inputRef}
      type="number"
      value={rawValue}
      onChange={(event) => {
        const nextValue = event.target.value;
        setRawValue(nextValue);

        if (nextValue === "") {
          onValueChange(0);
          return;
        }

        const parsed = Number(nextValue);
        if (Number.isFinite(parsed)) onValueChange(parsed);
      }}
      onBlur={(event) => {
        if (rawValue !== "" && !Number.isFinite(Number(rawValue))) {
          setRawValue(String(normalizedValue));
        }
        onBlur?.(event);
      }}
    />
  );
}
