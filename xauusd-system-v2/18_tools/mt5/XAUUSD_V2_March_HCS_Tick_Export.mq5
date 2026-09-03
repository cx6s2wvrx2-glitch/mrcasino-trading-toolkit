#property strict
#property script_show_inputs

input string InpSymbol = "XAUUSD!";
input string InpFileName = "xauusd_v2_march_hcs_ticks.csv";

struct TickWindowSpec
{
   string window_id;
   ulong  start_msc;
   ulong  end_msc_inclusive;
};

string ULongText(const ulong value)
{
   return StringFormat("%I64u", value);
}

string LongText(const long value)
{
   return StringFormat("%I64d", value);
}

void WriteStatusRow(
   const int handle,
   const string window_id,
   const string symbol,
   const ulong start_msc,
   const ulong end_msc_inclusive,
   const int copied,
   const int last_error
)
{
   FileWrite(
      handle,
      "xauusd_v2_mt5_terminal_tick_export_v1",
      "status",
      window_id,
      symbol,
      ULongText(start_msc),
      ULongText(end_msc_inclusive),
      IntegerToString(copied),
      IntegerToString(last_error),
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      ""
   );
}

void WriteTickRow(
   const int handle,
   const string window_id,
   const string symbol,
   const ulong start_msc,
   const ulong end_msc_inclusive,
   const int source_index,
   const MqlTick &tick,
   const int digits
)
{
   FileWrite(
      handle,
      "xauusd_v2_mt5_terminal_tick_export_v1",
      "tick",
      window_id,
      symbol,
      ULongText(start_msc),
      ULongText(end_msc_inclusive),
      "",
      "",
      IntegerToString(source_index),
      LongText(tick.time_msc),
      DoubleToString(tick.bid, digits),
      DoubleToString(tick.ask, digits),
      DoubleToString(tick.last, digits),
      ULongText(tick.volume),
      IntegerToString((int)tick.flags),
      DoubleToString(tick.volume_real, 8)
   );
}

void OnStart()
{
   if(StringLen(InpSymbol) == 0)
   {
      Print("XAUUSD V2 tick export blocked: symbol is empty");
      return;
   }

   if(!SymbolSelect(InpSymbol, true))
   {
      PrintFormat(
         "XAUUSD V2 tick export blocked: SymbolSelect(%s) failed, error=%d",
         InpSymbol,
         GetLastError()
      );
      return;
   }

   long digits_raw = 0;
   if(!SymbolInfoInteger(InpSymbol, SYMBOL_DIGITS, digits_raw))
   {
      PrintFormat(
         "XAUUSD V2 tick export blocked: SYMBOL_DIGITS unavailable for %s, error=%d",
         InpSymbol,
         GetLastError()
      );
      return;
   }
   const int digits = (int)digits_raw;

   ResetLastError();
   const int handle = FileOpen(InpFileName, FILE_WRITE | FILE_CSV | FILE_ANSI, ',');
   if(handle == INVALID_HANDLE)
   {
      PrintFormat(
         "XAUUSD V2 tick export blocked: FileOpen(%s) failed, error=%d",
         InpFileName,
         GetLastError()
      );
      return;
   }

   FileWrite(
      handle,
      "schema_version",
      "record_type",
      "window_id",
      "broker_symbol",
      "start_msc",
      "end_msc_inclusive",
      "copy_result",
      "last_error",
      "source_index",
      "time_msc",
      "bid",
      "ask",
      "last",
      "volume",
      "flags",
      "volume_real"
   );

   TickWindowSpec windows[2];
   windows[0].window_id = "buy_1975_hcs_candidate_2023_03_30_1231";
   windows[0].start_msc = 1680179460000;
   windows[0].end_msc_inclusive = 1680179519999;
   windows[1].window_id = "sell_1986_hcs_control_2023_03_31_1236";
   windows[1].start_msc = 1680266160000;
   windows[1].end_msc_inclusive = 1680266219999;

   for(int window_index = 0; window_index < ArraySize(windows); window_index++)
   {
      MqlTick ticks[];
      ResetLastError();
      const int copied = CopyTicksRange(
         InpSymbol,
         ticks,
         COPY_TICKS_ALL,
         windows[window_index].start_msc,
         windows[window_index].end_msc_inclusive
      );
      const int request_error = GetLastError();

      WriteStatusRow(
         handle,
         windows[window_index].window_id,
         InpSymbol,
         windows[window_index].start_msc,
         windows[window_index].end_msc_inclusive,
         copied,
         request_error
      );

      if(copied > 0)
      {
         const int available = ArraySize(ticks);
         const int write_count = MathMin(copied, available);
         for(int tick_index = 0; tick_index < write_count; tick_index++)
         {
            WriteTickRow(
               handle,
               windows[window_index].window_id,
               InpSymbol,
               windows[window_index].start_msc,
               windows[window_index].end_msc_inclusive,
               tick_index,
               ticks[tick_index],
               digits
            );
         }
      }

      FileFlush(handle);
      PrintFormat(
         "XAUUSD V2 tick export window=%s copied=%d error=%d",
         windows[window_index].window_id,
         copied,
         request_error
      );
   }

   FileClose(handle);
   PrintFormat(
      "XAUUSD V2 tick export complete: %s\\MQL5\\Files\\%s",
      TerminalInfoString(TERMINAL_DATA_PATH),
      InpFileName
   );
}
