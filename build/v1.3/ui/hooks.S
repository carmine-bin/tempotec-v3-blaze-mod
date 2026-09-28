# Validated MIPS32 little-endian UI hooks. No global UI state is introduced.
# Assembled by patch.py at VA 0x907040 in the verified empty RX/RW file gap.
# Every call uses the original executable's non-PIC direct-call convention.

hidden_bar:
 addiu sp, sp, -32
 sw ra, 28(sp)
 li a1, 0x80c9a8
 jal 0x449d00
 nop
 beq v0, zero, hidden_done
 nop
 lw v0, 4(v0)
 slt v0, v0, zero
hidden_done:
 lw ra, 28(sp)
 jr ra
 addiu sp, sp, 32

target_list:
 addiu v0, zero, 11
 beq a0, v0, target_yes
 addiu v0, zero, 19
 beq a0, v0, target_yes
 addiu v0, zero, 20
 beq a0, v0, target_yes
 addiu v0, zero, 97
 beq a0, v0, target_yes
 addiu v0, zero, 110
 beq a0, v0, target_yes
 nop
 jr ra
 move v0, zero
target_yes:
 jr ra
 addiu v0, zero, 1

# Replace only the basename of a resolved path. Theme-directory prefix and
# all 0x60 bytes of the registered widget contract after the path are retained.
basename:
 move t0, a0
 move t1, a0
 addiu t3, zero, 92
basename_loop:
 lbu t2, 0(t0)
 beq t2, zero, basename_copy
 addiu t0, t0, 1
 bne t2, t3, basename_loop
 nop
 b basename_loop
 move t1, t0
basename_copy:
 j 0x906f70
 move a0, t1

list_header:
 enter
 move s0, a0
 move s1, a2
 jal 0x4e1d80
 nop
 move s3, v0
 bne v0, zero, list_header_done
 nop
 jal target_list
 lw a0, 64(s0)
 beq v0, zero, list_header_done
 nop
 jal hidden_bar
 lw a0, 216(s0)
 beq v0, zero, list_header_done
 nop
 move a0, s1
 li a1, sub_filename
 jal basename
 nop
list_header_done:
 move v0, s3
 leave

# Called at the set-sub-back resolver site. Caller s1 is the activity;
# caller s3 is its owning view's name. Read them from our saved registers.
add_header:
 enter
 move s0, a1
 lw s1, 36(sp)
 lw s2, 28(sp)
 jal 0x4e7040
 nop
 move s3, v0
 bne v0, zero, add_header_done
 nop
 beq s2, zero, add_header_done
 nop
 move a0, s2
 li a1, add_name
 jal 0x9064e0
 nop
 bne v0, zero, add_header_done
 nop
 jal hidden_bar
 move a0, s1
 beq v0, zero, add_header_done
 nop
 move a0, s0
 li a1, set_filename
 jal basename
 nop
add_header_done:
 move v0, s3
 leave

# Caller s2 holds the EQ activity at this resolver site.
eq_header:
 enter
 move s0, a1
 lw s1, 32(sp)
 jal 0x50e480
 nop
 move s3, v0
 bne v0, zero, eq_header_done
 nop
 jal hidden_bar
 move a0, s1
 beq v0, zero, eq_header_done
 nop
 move a0, s0
 li a1, eq_filename
 jal basename
 nop
eq_header_done:
 move v0, s3
 leave

# Inline branch replacement. Only v0/v1 are used; no stack or call state.
list_geometry:
 bgez v0, list_geometry_keep
 nop
 lw v0, 64(s0)
 addiu v1, zero, 11
 beq v0, v1, list_geometry_keep
 addiu v1, zero, 19
 beq v0, v1, list_geometry_keep
 addiu v1, zero, 20
 beq v0, v1, list_geometry_keep
 addiu v1, zero, 97
 beq v0, v1, list_geometry_keep
 addiu v1, zero, 110
 beq v0, v1, list_geometry_keep
 nop
 j 0x4b5130
 lui a1, 0x83
list_geometry_keep:
 j 0x4b49b0
 lui a1, 0x83

# Replacement for the color close callback's tail call. Same launcher setting,
# same main activity, but an explicit transient origin for this reload only.
color_reload:
 enter
 addiu a0, zero, 12
 li a1, 0x80cdd4
 jal 0x430e60
 nop
 li a0, color_origin
 li a1, 0x80cde0
 jal 0x44d360
 nop
 move v0, zero
 leave

# Inline replacement at main-init's saved-navigation restoration branch.
# s0/activity and s1/language flag stay intact across strcmp/playback restore.
color_restore:
 lw a0, 372(s0)
 beq a0, zero, restore_original
 nop
 li a1, color_origin
 jal 0x9064e0
 nop
 bne v0, zero, restore_original
 nop
 addiu a1, sp, 24
 jal 0x514ec0
 move a0, s0
 j 0x51583c
 nop
restore_original:
 beq s1, zero, restore_music
 lui a1, 0x83
 j 0x5157d0
 nop
restore_music:
 j 0x515814
 nop

# Redirect only Settings visibility repaint; omit the defective narrow repaint.
# This call site supplies caller s0 = scrollbar context. Other lists take the
# exact original surface/rectangle path. No timer or geometry writes occur.
settings_repaint:
 enter
 lw t0, 40(sp)
 lw t1, 600(t0)
 beq t1, zero, settings_repaint_original
 nop
 lw t1, 64(t1)
 addiu t2, zero, 39
 bne t1, t2, settings_repaint_original
 nop
 lw a0, 12(t0)
 move a1, zero
settings_repaint_original:
 jal 0x46f320
 nop
 leave

sub_filename:
 .asciiz "ui_sub_back.view"
set_filename:
 .asciiz "ui_set_sub_back.view"
eq_filename:
 .asciiz "ui_eq_title.view"
add_name:
 .asciiz "vg_listview_add_m3u"
color_origin:
 .asciiz "ui_color_reload"
