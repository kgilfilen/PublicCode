// This is my C++ implementation of the CAVE algorithm; created for a major 
// telecommunications vendor for TDMA cell phone / customer service center 
// mutual authentication. This was added to the platform as a user-defined
// add-in method. Any identifying data has been removed.

// Kenny Gilfilen

// cave.cpp
#include <iostream>
using namespace std;

void CAVE(	const int number_of_rounds,
		int *offset_1,
		int *offset_2);

static void LFSR_cycle(void);

static void Rotate_right_registers(void);

static unsigned char bit_val(const unsigned char octet, const int bit)

unsigned long Auth_Signature(	const unsigned char RAND_CHALLENGE[4],
					const unsigned char AUTH_DATA[3],
					const unsigned char *SSD_AUTH,
					const int SAVE_REGISTERS);
#define LOMASK	0x0F
#define HIMASK	0xF0
#define TRUE	1
#define FALSE	0
#define LFSR_A	LFSR[0]
#define LFSR_B	LFSR[1]
#define LFSR_C	LFSR[2]
#define LFSR_D	LFSR[3]

unsigned char	Register[16];

unsigned char	SAVED_LFSR[4];
int			SAVED_OFFSET_1;
int			SAVED_OFFSET_2;
unsigned char	SAVED_RAND[4];
unsigned char	SAVED_DATA[4];

// authentication algorithm version (fixed)
unsigned char	AAV = {0xC7};

// external input data
unsigned char	ESN[4];

// saved outputs
unsigned char	LFSR[4];

// CAVE table
unsigned char	CaveTablev[256] =
	{
	d9, 23, 5f, e6, ca, 68, 97, b0, 7b, f2, 0c, 34, 11, a5, 8d, 4e,
	0a, 46, 77, 8d, 10, 9f, 5e, 62, f1, 34, ec, a5, c9, b3, d8, 2b,
	59, 47, e3, d2, ff, ae, 64, ca, 15, 8b, 7d, 38, 21, bc, 96, 00,
	49, 56, 23, 15, 97, e4, cb, 6f, f2, 70, 3c, 88, ba, d1, 0d, ae,
	e2, 38, ba, 44, 9f, 83, 5d, 1c, de, ab, c7, 65, f1, 76, 09, 20,
	86, bd, 0a, f1, 3c, a7, 29, 93, cb, 45, 5f, e8, 10, 74, 62, de,
	b8, 77, 80, d1, 12, 26, ac, 6d, e9, cf, f3, 54, 3a, 0b, 95, 4e,
	b1, 30, a4, 96, f8, 57, 49, 8e, 05, 1f, 62, 7c, c3, 2b, da, ed,
	bb, 86, 0d, 7a, 97, 13, 6c, 4e, 51, 30, e5, f2, 2f, d8, c4, a9,
	91, 76, f0, 17, 43, 38, 29, 84, a2, db, ef, 65, 5e, ca, 0d, bc,
	e7, fa, d8, 81, 6f, 00, 14, 42, 25, 7c, 5d, c9, 9e, b6, 33, ab,
	5a, 6f, 9b, d9, fe, 71, 44, c5, 37, a2, 88, 2d, 00, b6, 13, ec,
	4e, 96, a8, 5a, b5, d7, c3, 8d, 3f, f2, ec, 04, 60, 71, 1b, 29,
	04, 79, e3, c7, 1b, 66, 81, 4a, 25, 9d, dc, 5f, 3e, b0, f8, a2,
	91, 34, f6, 5c, 67, 89, 73, 05, 22, aa, cb, ee, bf, 18, d0, 4d,
	f5, 36, ae, 01, 2f, 94, c3, 49, 8b, bd, 58, 12, e0, 77, 6c, da
	}


int main()
{
	unsigned long Auth_Signature(	const unsigned char RAND_CHALLENGE[4],
						const unsigned char AUTH_DATA[3],
						const unsigned char *SSD_AUTH,
						const int SAVE_REGISTERS)

	{
		int i, offset_1, offset_2;
		unsigned long AUTH_SIGNATURE;
		for (i = 0; i < 4; i++)
		{
			LFSR[i] = RAND_CHALLENGE[i] ^ SSD_AUTH[i] ^ SSD_AUTH[i+4];		
		}

		if ((LFSR_A | LFSR_B | LFSR_C | LFSR_D) == 0)
		{
			for (i = 0; i < 4; i++) LFSR[i] = RAND_CHALLENGE[i];
		}

		// Load SSD_AUTH into r0-r7
		for (i = 0; i < 8; i++) Register[i] = SSD_AUTH[i];

		// Load the AAV into r8
		Register[8] = AAV;

		// Load AUTH_DATA into r9-r11
		for (i = 9; i < 12; i++) Register[i] = AUTH_DATA[i-9];

		// Load ESN into r12-r15
		for (i = 12; i < 16; i++) Register[i] = ESN[i-12];

		offset_1 = offset_2 = 128;
		CAVE(8, &offset_1, &offset_2);

		AUTH_SIGNATURE = 
			( (( unsigned long) (Register[0] ^ Register[13]) << 16) +
			  (( unsigned long) (Register[1] ^ Register[14]) <<  8) +
			  (( unsigned long) (Register[2] ^ Register[15])      ) )
			  & 0x3ffff;

		if (SAVE_REGISTERS)
		{
			// save LFSR offsets
			SAVED_OFFSET_1 = offset_1;
			SAVED_OFFSET_2 = offset_2;
			for (i = 12; i < 16; i++) 
			{
				SAVED_LFSR[i] = LFSR[i];
				SAVED_RAND[i] = RAND_CHALLENGE[i];
				if (i < 3)
				{SAVED_DATA[i] = AUTH_DATA[i];}
			}
		}
	}
	return (AUTH_SIGNATURE);
}


void CAVE(const int number_of_rounds,
		int *offset_1,
		int *offset_2);
{
	unsigned char	temp_reg0;
	unsigned char	lowNibble;
	unsigned char	hiNibble;
	unsigned char	temp;
	int			round_index;
	int			R_index;
	int			fail_count;
	unsigned char	T[16];

	for(	round_index = number_of_rounds - 1;
		round_index >= 0;
		round_index-- )
	{
	//hold r0 for use later
	temp_reg0 = Register[0];

	for(	R_index = 0; R_index < 16; R_index++ )
		{
			fail_count = 0;
			while(1)
			{
				*offset_1 += (LFSR_A ^ Register[R_index]);
				
				// will overflow; make to prevent.
				*offset_1 &= 0xFF;
				lowNibble = CaveTable[*offset_1 ] & LOMASK;
				if (lowNibble == (Register[R_index] & LOMASK ))
				{
					LFSR_cycle();
					fail_count++;
					if (fail_count == 32)
					{
						LFSR_D++;
						break;
					}
				}
				else break;
			}

			fail_count = 0;
			while(1)
			{
				*offset_2 += (LFSR_B ^ Register[R_index]);
				
				// will overflow; make to prevent.
				*offset_1 &= 0xFF;
				hiNibble = CaveTable[*offset_2 ] & HIMASK;
				if (lowNibble == (Register[R_index] & HIMASK ))
				{
					LFSR_cycle();
					fail_count++;
					if (fail_count == 32)
					{
						LFSR_D++;
						break;
					}
				}
				else break;
			}
			temp = lowNibble | hiNibble;
			if (R_index == 15)
				Register[R_index] = temp_reg0 ^ temp;
			else
				Register[R_index] = Register[R_index] ^ temp;

			LFSR_cycle();
		}

		Rotate_right_registers();
		for (R_index = 0; R_index < 16; R_index++)
		{
			temp = CaveTable[16 * round_index + R_index] & LOMASK;
			T[temp] = Register[R_index];
		}
		for (R_index = 0; R_index < 16; R_index++)
		{
			Register[R_index] = T[R_index];
		}
	}
}

static void LFSR_cycle(void)
{
	unsigned char temp;
	int i;

	temp  = bit_val(LFSR_B,6);
	temp ^= bit_val(LFSR_D,2);
	temp ^= bit_val(LFSR_D,1);
	temp ^= bit_val(LFSR_D,0);
	
	/*Shift right LFSR,Discard LFSR _D[0] bit */
	
	for ( i = 3; i > 0; i-- )
	{
	   LFSR[i] >>= 1;
	   if (LFSR[i - 1] & 0x01)
          LFSR[i] |= 0x80;
	}
	LFSR[0] >>= 1;

	LFSR_A |= temp;
}

static void Rotate_right_registers(void)
{
	unsigned int temp_reg;
	int i;
	
	temp_reg = Register[15];/*save lsb*/
	
	for (i = 15; i > 0; i-- )
	{
		Register[i] >>= 1;
		if (Register[i - 1] & 0x01)
		{
			Register[i] |= 0x80;

		}
	}

	Register[0] >>= 1;
	if (temp_reg & 0x01)
	{
		Register[0] |= 0x80;
	}
}

static unsigned char bit_val(const unsigned char octet, const int bit)
{
	return((octet << (7 - bit)) & 0x80);
}