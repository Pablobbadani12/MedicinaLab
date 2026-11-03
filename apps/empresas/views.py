from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Empresa
from .forms import EmpresaForm

@login_required
def empresa_list(request):
    empresas = Empresa.objects.all()
    return render(request, 'empresas/empresa_list.html', {'empresas': empresas})

@login_required
def empresa_create(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('empresas:empresa_list')
    else:
        form = EmpresaForm()
    return render(request, 'empresas/empresa_form.html', {'form': form})
