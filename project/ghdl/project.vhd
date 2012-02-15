--+============================================================================+
--|                                                                            |
--|                     This file was generated by Chips                       |
--|                                                                            |
--|                                  Chips                                     |
--|                                                                            |
--|                      http://github.com/dawsonjon/chips                     |
--|                                                                            |
--|                                                             Python powered |
--+============================================================================+

-- generated by python streams library
-- date generated  : UTC 2012-02-04 17:13:21
-- platform        : linux2
-- python version  : 2.7.2+ (default, Oct 4 2011, 20:06:09) [GCC 4.6.1]
-- streams version : 0.1.3

--+============================================================================+
--|                             **END OF HEADER**                              |
--+============================================================================+

--                                   ***                                       

--+============================================================================+
--|                    **START OF EXTERNAL DEPENDENCIES**                      |
--+============================================================================+



--+============================================================================+
--|                     **END OF EXTERNAL DEPENDENCIES**                       |
--+============================================================================+

--                                   ***                                       

--+============================================================================+
--|                     **START OF AUTO GENERATED CODE**                       |
--+============================================================================+

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity STREAMS_VHDL_MODEL is

end entity STREAMS_VHDL_MODEL;

architecture RTL of STREAMS_VHDL_MODEL is


  --returns the greater of the two parameters
  function MAX(
    A : integer;
    B : integer) return integer is
  begin
    if A > B then
      return A;
    else
      return B;
    end if;
  end MAX;

  --returns a std_logic_vector sum of the two parameters
  function ABSOLUTE(
    A : std_logic_vector) return std_logic_vector is
  begin
    return std_logic_vector(abs(signed(A)));
  end ABSOLUTE;

  --returns a std_logic_vector sum of the two parameters
  function ADD(
    A : std_logic_vector; 
    B : std_logic_vector) return std_logic_vector is
  begin
    return std_logic_vector(
      resize(signed(A), MAX(A'length, B'length) + 1) + 
      resize(signed(B), MAX(A'length, B'length) + 1));
    end ADD;

  --returns a std_logic_vector product of the two parameters
  function MUL(
    A : std_logic_vector; 
    B : std_logic_vector) return std_logic_vector is
  begin
    return std_logic_vector(
      signed(A) *
      signed(B));
    end MUL;

  --returns a std_logic_vector difference of the two parameters
  function SUB(
    A : std_logic_vector; 
    B : std_logic_vector) return std_logic_vector is
  begin
    return std_logic_vector(
      resize(signed(A), MAX(A'length, B'length) + 1) - 
      resize(signed(B), MAX(A'length, B'length) + 1));
  end SUB;

  --returns A shifted right (arithmetic) by A
  function SR(
    A  : std_logic_vector; 
    B : std_logic_vector) return std_logic_vector is
  begin
    return std_logic_vector(shift_right(signed(A), to_integer(signed(B))));
  end SR;

  --returns A shifted left by B
  function SL(
    A  : std_logic_vector; 
    B : std_logic_vector) return std_logic_vector is
  begin
    return std_logic_vector(shift_left(signed(A), to_integer(signed(B))));
  end SL;

  --returns bitwise and of A and B
  --(A and B are resized to the length of the larger first)
  function BAND(
    A : std_logic_vector; 
    B : std_logic_vector) return std_logic_vector is
  begin
    return std_logic_vector(
      resize(signed(A), MAX(A'LENGTH, B'LENGTH)) and
      resize(signed(B), MAX(A'LENGTH, B'LENGTH)));
  end BAND;

  --returns bitwise or of A and B
  --(A and B are resized to the length of the larger first)
  function BOR(
    A : std_logic_vector; 
    B : std_logic_vector) return std_logic_vector is
  begin
    return std_logic_vector(
      resize(signed(A), MAX(A'LENGTH, B'LENGTH)) or
      resize(signed(B), MAX(A'LENGTH, B'LENGTH)));
  end BOR;

  --returns bitwise xor of A and B
  --(A and B are resized to the length of the larger first)
  function BXOR(
    A : std_logic_vector; 
    B : std_logic_vector) return std_logic_vector is
  begin
    return std_logic_vector(
      resize(signed(A), MAX(A'LENGTH, B'LENGTH)) xor
      resize(signed(B), MAX(A'LENGTH, B'LENGTH)));
  end BXOR;

  --equality comparison of A and B
  --(A and B are resized to the length of the larger first)
  function EQ(
    A : std_logic_vector; 
    B : std_logic_vector) return std_logic_vector is
  begin
    if 
      resize(signed(A), MAX(A'LENGTH, B'LENGTH)) =
      resize(signed(B), MAX(A'LENGTH, B'LENGTH)) then
      return "1";
    else
      return "0";
    end if;
  end EQ;

  --inequality comparison of A and B
  --(A and B are resized to the length of the larger first)
  function NE(
    A : std_logic_vector; 
    B : std_logic_vector) return std_logic_vector is
  begin
    if 
    resize(signed(A), MAX(A'LENGTH, B'LENGTH)) /=
    resize(signed(B), MAX(A'LENGTH, B'LENGTH)) then
      return "1";
    else
      return "0";
    end if;
  end NE;

  --greater than comparison of A and B
  --(A and B are resized to the length of the larger first)
  function GT(
    A : std_logic_vector; 
    B : std_logic_vector) return std_logic_vector is
  begin
    if 
      resize(signed(A), MAX(A'LENGTH, B'LENGTH)) >
      resize(signed(B), MAX(A'LENGTH, B'LENGTH)) then
      return "1";
    else
      return "0";
    end if;
  end GT;

  --greater than or equal comparison of A and B
  --(A and B are resized to the length of the larger first)
  function GE(
    A : std_logic_vector; 
    B : std_logic_vector) return std_logic_vector is
  begin
    if 
      resize(signed(A), MAX(A'LENGTH, B'LENGTH)) >=
      resize(signed(B), MAX(A'LENGTH, B'LENGTH)) then
      return "1";
    else
      return "0";
    end if;
  end GE;

  --less than comparison of A and B
  --(A and B are resized to the length of the larger first)
  function LT(
    A : std_logic_vector; 
    B : std_logic_vector) return std_logic_vector is
  begin
    if 
      resize(signed(A), MAX(A'LENGTH, B'LENGTH)) <
      resize(signed(B), MAX(A'LENGTH, B'LENGTH)) then
      return "1";
    else
      return "0";
    end if;
  end LT;

  --less than or equal comparison of A and B
  --(A and B are resized to the length of the larger first)
  function LE(
    A : std_logic_vector; 
    B : std_logic_vector) return std_logic_vector is
  begin
    if 
      resize(signed(A), MAX(A'LENGTH, B'LENGTH)) <=
      resize(signed(B), MAX(A'LENGTH, B'LENGTH)) then
      return "1";
    else
      return "0";
    end if;
  end LE;

  --logical negation
  function LNOT(
    A : std_logic_vector) return std_logic_vector is
  begin
    if 
      A = std_logic_vector(to_signed(0, A'LENGTH)) then
      return "1";
    else
      return "0";
    end if;
  end LNOT;

  --resize A to B bits
  function STD_RESIZE(
    A : std_logic_vector; 
    B : integer) return std_logic_vector is
  begin
    return std_logic_vector(
      resize(signed(A), B));
  end STD_RESIZE;

  type BINARY_STATE_TYPE is (BINARY_INPUT, BINARY_OUTPUT);
  type UNARY_STATE_TYPE is (UNARY_INPUT, UNARY_OUTPUT);
  type TEE_STATE_TYPE is (TEE_INPUT_A, TEE_WAIT_YZ, TEE_WAIT_Y, TEE_WAIT_Z);
  type DIVIDER_STATE_TYPE is (READ_A_B, DIVIDE_1, DIVIDE_2, WRITE_Z);
  type SERIAL_IN_STATE_TYPE is (IDLE, START, RX0, RX1, RX2, RX3, RX4, RX5, RX6, RX7, STOP, OUTPUT_DATA);
  type SERIAL_OUT_STATE_TYPE is (IDLE, START, WAIT_EN, TX0, TX1, TX2, TX3, TX4, TX5, TX6, TX7, STOP);
  type PRINTER_STATE_TYPE is (INPUT_A, SHIFT, OUTPUT_SIGN, OUTPUT_Z, OUTPUT_NL);
  type HEX_PRINTER_STATE_TYPE is (INPUT_A, OUTPUT_SIGN, OUTPUT_DIGITS);

  constant TIMER_1us_MAX : integer := 49;
  signal TIMER_1us_COUNT : integer range 0 to TIMER_1us_MAX;
  signal TIMER_1us : std_logic;
  constant TIMER_10us_MAX : integer := 49;
  signal TIMER_10us_COUNT : integer range 0 to TIMER_1us_MAX;
  signal TIMER_10us : std_logic;
  constant TIMER_100us_MAX : integer := 49;
  signal TIMER_100us_COUNT : integer range 0 to TIMER_1us_MAX;
  signal TIMER_100us : std_logic;
  constant TIMER_1ms_MAX : integer := 49;
  signal TIMER_1ms_COUNT : integer range 0 to TIMER_1us_MAX;
  signal TIMER_1ms : std_logic;

  signal CLK : std_logic;
  signal RST : std_logic;
  --file: /home/jon/chips-compiler/compiler.py, line: 465
  --STREAM 2 Printer(0)
  signal STREAM_2     : std_logic_vector(7 downto 0);
  signal STREAM_2_STB : std_logic;
  signal STREAM_2_ACK : std_logic;
  signal SIGN_2       : std_logic;
  signal STATE_2      : PRINTER_STATE_TYPE;
  type SHIFTER_2_TYPE is array (0 to 9) of std_logic_vector(3 downto 0);
  signal BINARY_2     : std_logic_vector(39 downto 0);
  signal SHIFTER_2    : SHIFTER_2_TYPE;
  signal COUNT_2      : integer range 0 to 39;
  signal CURSOR_2     : integer range 0 to 9;

  signal STREAM_0       : std_logic_vector(31 downto 0);
  signal STREAM_0_STB   : std_logic;
  signal STREAM_0_ACK   : std_logic;
  constant OP_IMM_1 : std_logic_vector(2 downto 0) := "000";
  constant OP_MOVE_1 : std_logic_vector(2 downto 0) := "001";
  constant OP_LNOT_1 : std_logic_vector(2 downto 0) := "010";
  constant OP_JMPF_1 : std_logic_vector(2 downto 0) := "011";
  constant OP_JMP_1 : std_logic_vector(2 downto 0) := "100";
  constant OP_SUB_1 : std_logic_vector(2 downto 0) := "101";
  constant OP_NOOP_1 : std_logic_vector(2 downto 0) := "110";
  constant OP_WRITE_0_1 : std_logic_vector(2 downto 0) := "111";
  type PROCESS_1_STATE_TYPE is (STALL, EXECUTE, WRITE_STREAM_0);
  type INSTRUCTIONS_TYPE_1  is array (0 to 24) of std_logic_vector(36 downto 0);
  type REGISTERS_TYPE_1     is array (0 to 3) of std_logic_vector(31 downto 0);

  --Pipeline stage 0 outputs
  signal OPERATION_0_1  : std_logic_vector(2 downto 0);
  signal SRCA_0_1       : std_logic_vector(1 downto 0);
  signal SRCB_0_1       : std_logic_vector(1 downto 0);
  signal IMMEDIATE_0_1  : std_logic_vector(31 downto 0);
  --Pipeline stage 1 outputs
  signal OPERATION_1_1    : std_logic_vector(2 downto 0);
  signal IMMEDIATE_1_1    : std_logic_vector(31 downto 0);
  signal REGA_1_1         : std_logic_vector(31 downto 0);
  signal REGB_1_1         : std_logic_vector(31 downto 0);
  signal DEST_1_1         : std_logic_vector(1 downto 0);
  --Pipeline stage 2 outputs
  signal OPERATION_2_1    : std_logic_vector(2 downto 0);
  signal IMMEDIATE_2_1    : std_logic_vector(31 downto 0);
  signal REGA_2_1         : std_logic_vector(31 downto 0);
  signal REGB_2_1         : std_logic_vector(31 downto 0);
  signal DEST_2_1         : std_logic_vector(1 downto 0);
  signal PRODUCT_A_2_1    : signed(35 downto 0);
  signal PRODUCT_B_2_1    : signed(35 downto 0);
  signal PRODUCT_C_2_1    : signed(35 downto 0);
  signal PRODUCT_D_2_1    : signed(35 downto 0);
  --Pipeline stage 3 outputs
  signal RESULT_3_1       : std_logic_vector(31 downto 0);
  signal DEST_3_1         : std_logic_vector(1 downto 0);
  signal REGISTER_EN_3_1  : std_logic;
  signal STATE_1          : PROCESS_1_STATE_TYPE;
  signal PC_1             : unsigned(4 downto 0);
  signal ZERO_1           : std_logic;
  signal A_1              : std_logic_vector(31 downto 0);
  signal B_1              : std_logic_vector(31 downto 0);
  signal QUOTIENT_1       : std_logic_vector(31 downto 0);
  signal SHIFTER_1        : std_logic_vector(31 downto 0);
  signal REMAINDER_1      : std_logic_vector(31 downto 0);
  signal COUNT_1          : integer range 0 to 32;
  signal SIGN_1           : std_logic;
  signal INSTRUCTIONS_1   : INSTRUCTIONS_TYPE_1 := (
0 => OP_IMM_1 & "01" & "00000000000000000000000000000000", -- file: /home/jon/chips-compiler/compiler.py line: 292
1 => OP_IMM_1 & "10" & "00000000000000000000000000001010", -- file: /usr/local/lib/python2.7/dist-packages/chips/instruction.py line: 170
2 => OP_NOOP_1 & "00" & "00000000000000000000000000000000", -- file: None line: None
3 => OP_MOVE_1 & "01" & "00000000000000000000000000000010", -- file: /usr/local/lib/python2.7/dist-packages/chips/instruction.py line: 449
4 => OP_NOOP_1 & "00" & "00000000000000000000000000000000", -- file: None line: None
5 => OP_MOVE_1 & "10" & "00000000000000000000000000000001", -- file: /home/jon/chips-compiler/compiler.py line: 292
6 => OP_NOOP_1 & "00" & "00000000000000000000000000000000", -- file: None line: None
7 => OP_LNOT_1 & "10" & "00000000000000000000000000000000", -- file: /usr/local/lib/python2.7/dist-packages/chips/instruction.py line: 180
8 => OP_NOOP_1 & "00" & "00000000000000000000000000000000", -- file: None line: None
9 => OP_JMPF_1 & "10" & "00000000000000000000000000001100", -- file: None line: None
10 => OP_JMP_1 & "00" & "00000000000000000000000000010110", -- file: /usr/local/lib/python2.7/dist-packages/chips/__init__.py line: 100
11 => OP_JMP_1 & "00" & "00000000000000000000000000001100", -- file: None line: None
12 => OP_MOVE_1 & "10" & "00000000000000000000000000000001", -- file: /home/jon/chips-compiler/compiler.py line: 292
13 => OP_NOOP_1 & "00" & "00000000000000000000000000000000", -- file: None line: None
14 => OP_WRITE_0_1 & "10" & "00000000000000000000000000000000", -- file: /usr/local/lib/python2.7/dist-packages/chips/streams.py line: 865
15 => OP_MOVE_1 & "10" & "00000000000000000000000000000001", -- file: /home/jon/chips-compiler/compiler.py line: 292
16 => OP_IMM_1 & "11" & "00000000000000000000000000000001", -- file: /usr/local/lib/python2.7/dist-packages/chips/instruction.py line: 170
17 => OP_NOOP_1 & "00" & "00000000000000000000000000000000", -- file: None line: None
18 => OP_SUB_1 & "10" & "00000000000000000000000000000011", -- file: /usr/local/lib/python2.7/dist-packages/chips/instruction.py line: 188
19 => OP_NOOP_1 & "00" & "00000000000000000000000000000000", -- file: None line: None
20 => OP_MOVE_1 & "01" & "00000000000000000000000000000010", -- file: /usr/local/lib/python2.7/dist-packages/chips/instruction.py line: 449
21 => OP_JMP_1 & "00" & "00000000000000000000000000000100", -- file: /usr/local/lib/python2.7/dist-packages/chips/__init__.py line: 101
22 => OP_JMP_1 & "00" & "00000000000000000000000000010110", -- file: None line: None
23 => OP_NOOP_1 & "00" & "00000000000000000000000000000000", -- file: None line: None
24 => OP_NOOP_1 & "00" & "00000000000000000000000000000000"); -- file: None line: None
  signal MOD_DIV_1        : std_logic;

begin

  process
  begin
    wait until rising_edge(CLK);
    TIMER_1us <= '0';
    TIMER_10us <= '0';
    TIMER_100us <= '0';
    TIMER_1ms <= '0';
    if TIMER_1us_COUNT = 0 then
       TIMER_1us_COUNT <= TIMER_1us_MAX;
       TIMER_1us <= '1';
       if TIMER_10us_COUNT = 0 then
         TIMER_10us_COUNT <= TIMER_10us_MAX;
         TIMER_10us <= '1';
         if TIMER_100us_COUNT = 0 then
           TIMER_100us_COUNT <= TIMER_100us_MAX;
           TIMER_100us <= '1';
           if TIMER_1ms_COUNT = 0 then
             TIMER_1ms_COUNT <= TIMER_1ms_MAX;
             TIMER_1ms <= '1';
           else
             TIMER_1ms_COUNT <= TIMER_1ms_COUNT - 1;
           end if;
         else
           TIMER_100us_COUNT <= TIMER_100us_COUNT - 1;
         end if;
       else
         TIMER_10us_COUNT <= TIMER_10us_COUNT - 1;
       end if;
    else
       TIMER_1us_COUNT <= TIMER_1us_COUNT - 1;
    end if;
    if RST = '1' then
       TIMER_1us_COUNT <= TIMER_1us_MAX;
       TIMER_1us <= '0';
       TIMER_10us_COUNT <= TIMER_10us_MAX;
       TIMER_10us <= '0';
       TIMER_100us_COUNT <= TIMER_100us_MAX;
       TIMER_100us <= '0';
       TIMER_1ms_COUNT <= TIMER_1ms_MAX;
       TIMER_1ms <= '0';
    end if;
  end process;

  --internal clock generator
  process
  begin
    while True loop
      CLK <= '0';
      wait for 5 ns;
      CLK <= '1';
      wait for 5 ns;
    end loop;
    wait;
  end process;

  --internal reset generator
  process
  begin
    RST <= '1';
    wait for 20 ns;
    RST <= '0';
    wait;
  end process;

  --file: /home/jon/chips-compiler/compiler.py, line: 465
  --Console(2)
  process
    variable OUTPUT_LINE : line;
    variable INT  : integer;
    variable CHAR : character;
  begin
    wait until rising_edge(CLK);
    STREAM_2_ACK <= '0';
    if STREAM_2_STB = '1' and STREAM_2_ACK = '0' then
      INT := (to_integer(unsigned(STREAM_2)));
      CHAR := character'val (INT);
      if INT = 10 then
        writeline(output, OUTPUT_LINE);
      else
        write(OUTPUT_LINE, CHAR);
      end if;
      STREAM_2_ACK <= '1';
    end if;
  end process;

  --file: /home/jon/chips-compiler/compiler.py, line: 465
  --STREAM 2 Printer(0)
  process
    variable CARRY_2 : std_logic_vector(10 downto 0);
  begin
    wait until rising_edge(CLK);
    case STATE_2 is
      when INPUT_A =>
        if STREAM_0_STB = '1' then
          STREAM_0_ACK <= '1';
          SIGN_2 <= STREAM_0(31);
          SHIFTER_2 <= (others => "0000");
          BINARY_2 <= STD_RESIZE(ABSOLUTE(STREAM_0), 40);
          COUNT_2 <= 39;
          STATE_2 <= SHIFT;
        end if;

      when SHIFT =>
        STREAM_0_ACK <= '0';
        CARRY_2 := (Others => '0');
        CARRY_2(0) := BINARY_2(39);
        for DIGIT in 0 to 9 loop
            case SHIFTER_2(DIGIT) is
                when "0101" =>
                  CARRY_2(DIGIT+1) := '1';
                  SHIFTER_2(DIGIT) <= "000" & CARRY_2(DIGIT);
                when "0110" =>
                  CARRY_2(DIGIT+1) := '1';
                  SHIFTER_2(DIGIT) <= "001" & CARRY_2(DIGIT);
                when "0111" =>
                  CARRY_2(DIGIT+1) := '1';
                  SHIFTER_2(DIGIT) <= "010" & CARRY_2(DIGIT);
                when "1000" =>
                  CARRY_2(DIGIT+1) := '1';
                  SHIFTER_2(DIGIT) <= "011" & CARRY_2(DIGIT);
                when "1001" =>
                  CARRY_2(DIGIT+1) := '1';
                  SHIFTER_2(DIGIT) <= "100" & CARRY_2(DIGIT);
                when others =>
                  CARRY_2(DIGIT+1) := '0';
                  SHIFTER_2(DIGIT) <= SHIFTER_2(DIGIT)(2 downto 0) & CARRY_2(DIGIT);
            end case;
        end loop;
        BINARY_2 <= BINARY_2(38 downto 0) & '0';
        if COUNT_2 = 0 then
          STATE_2 <= OUTPUT_SIGN;
          CURSOR_2 <= 9;
        else
          COUNT_2 <= COUNT_2 - 1;
        end if;

      when OUTPUT_SIGN =>
        if SIGN_2 = '1' then
          STREAM_2 <= "00101101";
          STREAM_2_STB <= '1';
          if STREAM_2_ACK = '1' then
            STREAM_2_STB <= '0';
            STATE_2 <= OUTPUT_Z;
          end if;
        else
          STATE_2 <= OUTPUT_Z;
        end if;

      when OUTPUT_Z =>
        STREAM_2_STB <= '1';
        STREAM_2 <= "0011" & SHIFTER_2(CURSOR_2);
        if STREAM_2_ACK = '1' then
          STREAM_2_STB <= '0';
          if CURSOR_2 = 0 then
            STATE_2 <= OUTPUT_NL;
          else
            CURSOR_2 <= CURSOR_2 - 1;
          end if;
        end if;

      when OUTPUT_NL =>
        STREAM_2_STB <= '1';
        STREAM_2 <= X"0A";
        if STREAM_2_ACK = '1' then
          STREAM_2_STB <= '0';
          STATE_2 <= INPUT_A;
        end if;

     end case;
     if RST = '1' then
       STREAM_2_STB <= '0';
       STREAM_0_ACK <= '0';
       STATE_2 <= INPUT_A;
     end if;
  end process;

  -- PIPELINE STAGE 0 - INSTRUCTION FETCH
  process
    variable INSTRUCTION : std_logic_vector(36 downto 0);
  begin
    wait until rising_edge(CLK);
      INSTRUCTION := INSTRUCTIONS_1(to_integer(PC_1));
      SRCA_0_1      <= INSTRUCTION(33 downto 32);
      SRCB_0_1      <= INSTRUCTION(1 downto 0);
      IMMEDIATE_0_1 <= INSTRUCTION(31 downto 0);
      OPERATION_0_1 <= INSTRUCTION(36 downto 34);
  end process;

  -- PIPELINE STAGE 1 - REGISTER FETCH
  process
    variable REGISTERS : REGISTERS_TYPE_1;
  begin
    wait until rising_edge(CLK);
    if REGISTER_EN_3_1 = '1' then
      REGISTERS(to_integer(unsigned(DEST_3_1))) := RESULT_3_1;
    end if;
    if STATE_1 = EXECUTE or STATE_1 = STALL then
      REGA_1_1      <= REGISTERS(to_integer(unsigned(SRCA_0_1)));
      REGB_1_1      <= REGISTERS(to_integer(unsigned(SRCB_0_1)));
      DEST_1_1      <= SRCA_0_1;
      OPERATION_1_1 <= OPERATION_0_1;
      IMMEDIATE_1_1 <= IMMEDIATE_0_1;
    end if;
  end process;

  -- PIPELINE STAGE 2 - PRE_EXECUTE
  REGA_2_1      <= REGA_1_1;
  REGB_2_1      <= REGB_1_1;
  DEST_2_1      <= DEST_1_1;
  OPERATION_2_1 <= OPERATION_1_1;
  IMMEDIATE_2_1 <= IMMEDIATE_1_1;

  -- PIPELINE STAGE 3 - EXECUTE
  process
    variable MODULO       : unsigned(31 downto 0);
    variable STALL_COUNT  : integer range 0 to 1;
  begin
    wait until rising_edge(CLK);
    REGISTER_EN_3_1 <= '0';
    case STATE_1 is
      when STALL =>
        PC_1 <= PC_1 + 1;
        if STALL_COUNT = 0 then
          STATE_1 <= EXECUTE;
        else
          STALL_COUNT := STALL_COUNT - 1;
        end if;
      when EXECUTE =>
        DEST_3_1 <= DEST_2_1;
        RESULT_3_1 <= REGA_2_1;
        PC_1 <= PC_1 + 1;

        --execute instructions
        case OPERATION_2_1 is
          when OP_MOVE_1 => 
            RESULT_3_1 <= REGB_2_1;
            REGISTER_EN_3_1 <= '1';
          when OP_NOOP_1 => 
            REGISTER_EN_3_1 <= '0';
            RESULT_3_1 <= RESULT_3_1;
          when OP_SUB_1  => 
            RESULT_3_1 <= STD_RESIZE( SUB(REGA_2_1, REGB_2_1), 32);
            REGISTER_EN_3_1 <= '1';
          when OP_IMM_1  => 
            RESULT_3_1 <= STD_RESIZE(IMMEDIATE_2_1, 32);
            REGISTER_EN_3_1 <= '1';
          when OP_LNOT_1  => 
            RESULT_3_1 <= STD_RESIZE( LNOT(REGA_2_1), 32);
            REGISTER_EN_3_1 <= '1';
          when OP_JMP_1 =>
            STATE_1 <= STALL;
            STALL_COUNT := 1;
            PC_1 <= resize(unsigned(IMMEDIATE_2_1), 5);
          when OP_JMPF_1 =>
            if RESULT_3_1 = "00000000000000000000000000000000" then
              STATE_1 <= STALL;
              STALL_COUNT := 1;
              PC_1 <= resize(unsigned(IMMEDIATE_2_1), 5);
            end if;
          when OP_WRITE_0_1 =>
            STATE_1 <= WRITE_STREAM_0;
            STREAM_0 <= STD_RESIZE(REGA_2_1, 32);
            STREAM_0_STB <= '1';
            PC_1 <= PC_1;
          when others => null;
        end case;

      when WRITE_STREAM_0 =>
        STREAM_0_STB <= '1';
        if STREAM_0_ACK = '1' then
          STREAM_0_STB <= '0';
          STATE_1 <= EXECUTE;
          PC_1 <= PC_1 + 1;
        end if;
    end case;

    if RST = '1' then
      STATE_1 <= STALL;
      STALL_COUNT := 1;
      PC_1 <= "00000";
      STREAM_0_STB <= '0';
    end if;
  end process;



end architecture RTL;

--+============================================================================+
--|                       **END OF AUTO GENERATED CODE**                       |
--+============================================================================+